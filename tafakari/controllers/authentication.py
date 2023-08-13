from http import HTTPStatus
from typing import Optional, Any

import pendulum
import redis
from flask import Blueprint, jsonify
from flask_jwt_extended import create_access_token, get_jwt, jwt_required
from flask_pydantic import validate
from sqlalchemy import and_, exc

from .schemas import UserRequestSchema, UserProfileViewSchema
from ..extensions import jwt
from ..models.users import User, check_password
from ...configs import configs

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


@authentications.route("/login", methods=["POST"])
@validate(body=UserRequestSchema)
def login(body: UserRequestSchema):
    user = User.query.filter(
        and_(
            User.username == body.username,
            User.email == body.email,
        )
    ).first()

    if user and check_password(user.password, body.password):
        token = create_access_token(identity=user.username, fresh=True)
        return (
            jsonify(
                access_token=token,
                expires=str(configs.JWT_ACCESS_TOKEN_EXPIRES.seconds),
                username=user.username,
            ),
            HTTPStatus.ACCEPTED,
        )

    if not user:
        return (
            jsonify(
                message="No user registered with those credentials. Please register to begin"
            ),
            HTTPStatus.UNAUTHORIZED,
        )

    return jsonify(message="Incorrect Credentials"), HTTPStatus.UNAUTHORIZED


@authentications.route("/logout", methods=["DELETE"])
@jwt_required(fresh=True)
def logout():
    jti = get_jwt()["jti"]
    jwt_redis_blocklist.set(jti, "", ex=configs.JWT_ACCESS_TOKEN_EXPIRES)
    return jsonify(message="Access token revoked"), HTTPStatus.OK


@authentications.route("/register", methods=["POST"])
@validate(body=UserRequestSchema)
def register(body: UserRequestSchema):
    existing_user: User = User.query.filter(
        and_(User.username == body.username, User.email == body.email)
    ).first()

    if existing_user:
        return jsonify(message="User already exists"), HTTPStatus.CONFLICT

    if body.is_admin:
        new_user = User.create(
            username=body.username,
            email=body.email,
            password=body.password,
            is_admin=body.is_admin,
        )
        new_user.save()

        return UserProfileViewSchema.from_orm(new_user).dict(), HTTPStatus.CREATED

    try:
        new_user = User.create(
            username=body.username, email=body.email, password=body.password
        )

        return UserProfileViewSchema.from_orm(new_user).dict(), HTTPStatus.CREATED

    except exc.IntegrityError as exception:
        return (
            jsonify(message="A user with the same credentials is registered"),
            HTTPStatus.CONFLICT,
        )
