from http import HTTPStatus

from flask import Blueprint, jsonify
from flask_jwt_extended import current_user, jwt_required
from sqlalchemy import and_

from ..models.subreddit import Subreddit
from ..models.users import User
from .schemas import UserProfileViewSchema

user = Blueprint("user", __name__)


@user.route("/get/profile", methods=["GET"])
@jwt_required(fresh=True)
def get_profile():
    if current_user:
        user_profile = User.query.filter(
            and_(
                User.username == current_user.username,
                User.email == current_user.email
            )
        ).join(
            Subreddit, User.id == Subreddit.created_by, isouter=True
        ).first()

        if user_profile:
            print(user_profile.post)
            return UserProfileViewSchema.from_orm(
                user_profile
            ).dict(
                exclude_none=True,
                exclude_unset=True
            ), HTTPStatus.ACCEPTED

    return jsonify(
        message="User not Found"
    ), HTTPStatus.NOT_FOUND
