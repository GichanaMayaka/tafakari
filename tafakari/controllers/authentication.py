from http import HTTPStatus
from typing import Any, Optional

import pendulum
import redis
from flask import Blueprint, Response, current_app, jsonify, request
from flask_jwt_extended import create_access_token, current_user, get_jwt, jwt_required
from flask_pydantic import validate
from sqlalchemy import and_, exc

from tafakari.configs import configs

from ..extensions import jwt, limiter
from ..models.users import User, check_password
from ..utils import get_client_ip_address, get_logger_instance
from .schemas import UserRequestSchema, UserViewSchema

authentications = Blueprint("authentication", __name__, url_prefix="/auth")

jwt_redis_blocklist = redis.StrictRedis(
    host=configs.REDIS_HOSTNAME, port=configs.REDIS_PORT, db=0, decode_responses=True
)


@jwt.user_identity_loader
def user_identity_lookup(user) -> User:
    return user


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data) -> Optional[User]:
    identity = jwt_data["sub"]
    return User.query.filter_by(username=identity).one_or_none()


@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header: dict, jwt_payload: dict) -> bool:
    jti = jwt_payload["jti"]
    token_in_redis = jwt_redis_blocklist.get(jti)
    return token_in_redis is not None


@jwt.additional_claims_loader
def add_additional_claims(identity: Any):
    return dict(exp=pendulum.now() + configs.JWT_ACCESS_TOKEN_EXPIRES)


# TODO: Implement delete/deactivate profile as well as update profile
# TODO: Implement profile picture uploads
@authentications.route("/login", methods=["POST"])
@limiter.limit("3/minute")
@validate(body=UserRequestSchema)
def login(body: UserRequestSchema) -> tuple[Response, int]:
    """Signs in using details supplied in the body parameter

    Args:
        body (UserRequestSchema): The Request Details in JSON format

    Returns:
        tuple[Response, int]: The Response Object and Status Code
    """
    logger = get_logger_instance(current_app)
    request_ip_address = get_client_ip_address(request)

    user: User = User.query.filter(
        and_(
            User.username == body.username,
            User.email == body.email,
        )
    ).first()
    logger.info(
        "Retrieving User data for username %s from the database.",
        body.username,
    )

    if user and check_password(user.password, body.password):
        token = create_access_token(identity=user.username, fresh=True)
        logger.info(
            "User with username %s successfully logged in from IP address %s",
            user.username,
            request_ip_address,
        )
        return (
            jsonify(
                access_token=token,
                expires=str(configs.JWT_ACCESS_TOKEN_EXPIRES.seconds),
                username=user.username,
            ),
            HTTPStatus.ACCEPTED,
        )

    if not user:
        logger.warning(
            "Failed login attempt for username %s from IP address %s. No User Found with the credentials",
            body.username,
            request_ip_address,
        )
        return (
            jsonify(
                message="No user registered with those credentials. Please register to begin"
            ),
            HTTPStatus.FORBIDDEN,
        )

    logger.error(
        "Invalid credentials provided for user %s from IP address %s",
        body.username,
        request_ip_address,
    )
    return jsonify(message="Incorrect Credentials"), HTTPStatus.UNAUTHORIZED


@authentications.route("/logout", methods=["DELETE"])
@jwt_required(fresh=True)
@limiter.exempt
def logout() -> tuple[Response, int]:
    """Signs out the current user

    Returns:
        tuple[Response, int]: The Response Object and Status Code
    """
    logger = get_logger_instance(current_app)

    jti = get_jwt()["jti"]
    jwt_redis_blocklist.set(jti, "", ex=configs.JWT_ACCESS_TOKEN_EXPIRES)
    logger.info("User %s Successfully Signed-Out", current_user.username)
    return jsonify(message="Access token revoked"), HTTPStatus.OK


@authentications.route("/register", methods=["POST"])
@validate(body=UserRequestSchema)
def register(body: UserRequestSchema) -> tuple[Response, int]:
    """Registers a User based on the supplied details

    Args:
        body (UserRequestSchema): The Request details in JSON format

    Returns:
        tuple[Response, int]: The Response Object and Status Code
    """
    logger = get_logger_instance(current_app)

    logger.info("Checking for duplicate user")
    existing_user = User.query.filter(
        and_(User.username == body.username, User.email == body.email)
    ).first()

    if existing_user:
        logger.warning(
            "Duplicate user found using username: %s, and email: %s",
            body.username,
            body.email,
        )
        return jsonify(message="User already exists"), HTTPStatus.CONFLICT

    if body.is_admin:
        new_user = User.create(
            username=body.username,
            email=body.email,
            password=body.password,
            is_admin=body.is_admin,
        )
        new_user.save()

        logger.info("Successfully registered user: %s", new_user.username)
        return jsonify(UserViewSchema.from_orm(new_user).dict()), HTTPStatus.CREATED

    try:
        new_user = User.create(
            username=body.username, email=body.email, password=body.password
        )

        logger.info("Successfully registered user: %s", new_user.username)
        return jsonify(UserViewSchema.from_orm(new_user).dict()), HTTPStatus.CREATED

    except exc.IntegrityError:
        logger.warning(
            "Duplicate user found using username: %s, and email: %s",
            body.username,
            body.email,
        )
        return (
            jsonify(message="A user with the same credentials is registered."),
            HTTPStatus.CONFLICT,
        )
