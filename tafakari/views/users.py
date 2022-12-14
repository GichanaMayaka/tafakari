from http import HTTPStatus

from flask import Blueprint, jsonify
from flask_jwt_extended import current_user, jwt_required
from flask_pydantic import validate
from sqlalchemy import and_

from ..models.users import User
from .schemas import UserProfileViewSchema

user = Blueprint("user", __name__, template_folder="templates")


@user.route("/get/profile", methods=["GET"])
@jwt_required()
def get_profile():
    if current_user:
        user_profile = User.query.filter(
            and_(
                User.username == current_user.username,
                User.email == current_user.email
            )
        ).first()

        if user_profile:
            return jsonify(
                profile=user_profile.to_dict()
            ), HTTPStatus.FOUND

    return jsonify(
        message="User not Found"
    ), HTTPStatus.NOT_FOUND
