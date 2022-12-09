import datetime
from gettext import gettext
from http import HTTPStatus

from flask import Blueprint, jsonify, flash, redirect, url_for
from flask_jwt_extended import create_access_token
from flask_login import login_user, login_required, logout_user, current_user
from flask_pydantic import validate
from sqlalchemy import and_

from .schemas import UserRequestSchema
from ..database import db
from ..extensions import login_manager
from ..models.users import User, check_password

authentications = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth"
)


@login_manager.user_loader
def load_user(user_id: int):
    return User.get_by_id(user_id)


@login_manager.unauthorized_handler
def handler():
    return jsonify(
        message="Please login to continue"
    ), HTTPStatus.UNAUTHORIZED


@authentications.route("/login", methods=["POST"])
@validate(body=UserRequestSchema)
def auth(body: UserRequestSchema):
    user = User.query.filter(
        and_(
            User.username == body.username,
            User.email == body.email,
        )
    ).first()

    if user and check_password(user.password, body.password):
        token = create_access_token(identity=user.username)
        login_user(user, duration=datetime.timedelta(minutes=30))
        return jsonify(access_token=token), HTTPStatus.ACCEPTED

    elif not user:
        return jsonify(
            message="No user registered with those credentials. Please register to begin"), HTTPStatus.UNAUTHORIZED

    return jsonify(message="Incorrect Credentials"), HTTPStatus.UNAUTHORIZED


@authentications.route("/logout", methods=["GET"])
@login_required
def logout():
    if current_user:
        logout_user()
        flash(gettext('You were logged out'), 'success')
        return jsonify(message="successfully logged out")
        # return redirect(url_for('auth.login'))
    return redirect(url_for("auth.login"))


@authentications.route("/register", methods=["GET", "POST"])
@validate(body=UserRequestSchema)
def create_user(body: UserRequestSchema):
    existing_user = User.query.filter(
        and_(
            User.username == body.username,
            User.email == body.email
        )
    ).first()

    if existing_user:
        return jsonify(message="User already exists"), HTTPStatus.CONFLICT

    else:
        if body.is_admin:
            new_user = User.create(username=body.username, email=body.email, password=body.password,
                                   is_admin=body.is_admin)
            db.session.add(new_user)
            db.session.commit()

            return jsonify(user=new_user.to_dict()), HTTPStatus.CREATED

        new_user = User.create(username=body.username, email=body.email, password=body.password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify(user=new_user.to_dict()), HTTPStatus.CREATED
