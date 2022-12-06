from flask import Blueprint, jsonify, request
from flask_pydantic import validate
from ..models.users import User
from .schemas import UserRequestSchema

user = Blueprint("user", __name__, template_folder="templates")


@user.route("/user", methods=["POST"])
@validate(body=UserRequestSchema)
def create_user(body: UserRequestSchema):
    u = User.query.filter_by(username=body.username).all()

    return {
        "user": str(u)
    }
