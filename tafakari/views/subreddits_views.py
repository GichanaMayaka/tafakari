import pendulum
from flask import Blueprint
from flask_pydantic import validate
from sqlalchemy import and_

from .schemas import CreateSubredditPostSchema, UserRequestSchema, PostsRequestSchema
from ..database import db
from ..models.subreddit import Subreddit
from ..models.users import User
from ..models.posts import Post

subreddits = Blueprint("subreddit", __name__, template_folder="templates")


@subreddits.route("/create/subreddit", methods=["POST"])
@validate(body=CreateSubredditPostSchema)
def create_subreddit(body: CreateSubredditPostSchema):
    subreddit = Subreddit.query.filter_by(name=body.name).first()

    if not subreddit:
        new_subreddit = Subreddit(
            name=body.name,
            description=body.description,
        )
        user = User.query.filter_by(username="gichana").first()
        new_subreddit.created_by = user.id

        db.session.add(new_subreddit)
        db.session.commit()

        return {
            "message": "Created"
        }, 200

    return {
        "message": f"A subreddit with the title: {body.name}, already exists"
    }, 409


@subreddits.route("/get/subreddit", methods=["GET"])
def get_all_subreddits():
    all_subs = Subreddit.query.all()

    if all_subs:
        return {
            "subreddits": [{"id": sub.id, "name": sub.name} for sub in all_subs]
        }, 200

    return {
        "message": "No Subreddits"
    }, 404


@subreddits.route("/get/subreddit/<subreddit_id>", methods=["GET"])
def get_subreddit_by_id(subreddit_id: int):
    subreddit = Subreddit.query.filter_by(id=subreddit_id).first()

    if subreddit:
        user = User.query.filter_by(id=subreddit.created_by).first()

        return {
            "subreddit": {
                "name": subreddit.name,
                "description": subreddit.description,
                "created_by": user.username,
                "created_on": subreddit.created_on
            }
        }, 200

    return {
        "message": "No Subreddit Found"
    }, 404


@subreddits.route("/join/subreddit/<subreddit_id>", methods=["GET"])
def join_a_subreddit(subreddit_id: int):
    subreddit = Subreddit.query.filter_by(id=subreddit_id).first()

    if subreddit:
        user = User.query.filter_by(username="gichana").first()

        subreddit.users.append(user)

        db.session.add(subreddit)
        db.session.commit()

        return {
            "message": f"Successfully joined {subreddit.name}",
            "time_of_join": f"{pendulum.now()}"
        }, 200

    return {
        "message": "Subreddit Not Found"
    }, 404


@subreddits.route("/delete/subreddit/<subreddit_id>", methods=["DELETE"])
@validate(body=UserRequestSchema)
def delete_a_subreddit(subreddit_id: int, body: UserRequestSchema):
    creator_id = User.query.filter_by(username=body.username).first()

    if creator_id:
        subreddit_creator = Subreddit.query.filter(
            and_(Subreddit.id == subreddit_id, Subreddit.created_by == creator_id.id)
        ).first()
        if subreddit_creator:
            db.session.delete(subreddit_creator)
            db.session.commit()
            return {
                "message": "Subreddit Deleted"
            }, 202

    return {
        "message": "You are not authorised to delete this subreddit"
    }, 403
