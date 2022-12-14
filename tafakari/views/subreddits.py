from http import HTTPStatus

import pendulum
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, current_user
from flask_pydantic import validate
from sqlalchemy import and_

from .schemas import CreateSubredditPostSchema, UserRequestSchema
from ..models.subreddit import Subreddit
from ..models.users import User

subreddits = Blueprint("subreddit", __name__, template_folder="templates")


@subreddits.route("/create/subreddit", methods=["POST"])
@jwt_required(fresh=True)
@validate(body=CreateSubredditPostSchema)
def create_subreddit(body: CreateSubredditPostSchema):
    subreddit = Subreddit.query.filter_by(name=body.name).first()

    if not subreddit and current_user:
        new_subreddit = Subreddit.create(
            name=body.name,
            description=body.description,
            created_by=current_user.id
        )

        new_subreddit.save()

        return jsonify(message="created"), HTTPStatus.OK

    return jsonify(message=f"A subreddit with the title: {body.name}, already exists"), HTTPStatus.CONFLICT


@subreddits.route("/get/subreddit", methods=["GET"])
def get_all_subreddits():
    all_subs = Subreddit.query.all()

    if all_subs:
        return {
            "subreddits": [{"id": sub.id, "name": sub.name} for sub in all_subs]
        }, HTTPStatus.OK

    return {
        "message": "No Subreddits"
    }, HTTPStatus.NOT_FOUND


@subreddits.route("/get/subreddit/<subreddit_id>", methods=["GET"])
def get_subreddit_by_id(subreddit_id: int):
    subreddit = Subreddit.get_by_id(subreddit_id)

    if subreddit:
        user = User.get_by_id(subreddit.created_by)

        return {
            "subreddit": {
                "name": subreddit.name,
                "description": subreddit.description,
                "created_by": user.username,
                "created_on": subreddit.created_on
            }
        }, HTTPStatus.OK

    return {
        "message": "No Subreddit Found"
    }, HTTPStatus.NOT_FOUND


@subreddits.route("/join/subreddit/<subreddit_id>", methods=["GET"])
@jwt_required(fresh=True)
def join_a_subreddit(subreddit_id: int):
    subreddit = Subreddit.get_by_id(subreddit_id)

    if subreddit and current_user:
        subreddit.users.append(current_user)

        subreddit.save()

        return {
            "message": f"Successfully joined {subreddit.name}",
            "time_of_join": f"{pendulum.now()}"
        }, HTTPStatus.OK

    return {
        "message": "Subreddit Not Found"
    }, HTTPStatus.NOT_FOUND


@subreddits.route("/delete/subreddit/<subreddit_id>", methods=["DELETE"])
@validate(body=UserRequestSchema)
def delete_a_subreddit(subreddit_id: int, body: UserRequestSchema):
    creator_id = User.query.filter_by(username=body.username).first()

    if creator_id:
        subreddit_creator = Subreddit.query.filter(
            and_(Subreddit.id == subreddit_id, Subreddit.created_by == creator_id.id)
        ).first()
        if subreddit_creator:
            subreddit_creator.delete()

            return {
                "message": "Subreddit Deleted"
            }, HTTPStatus.ACCEPTED

    return {
        "message": "You are not authorised to delete this subreddit"
    }, HTTPStatus.FORBIDDEN
