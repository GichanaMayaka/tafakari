from http import HTTPStatus

from flask import Blueprint, jsonify
from flask_jwt_extended import current_user, jwt_required

from ..models.posts import Post
from ..models.subreddit import Subreddit
from ..models.users import User
from .schemas import (
    AllPostsViewSchema,
    AllSubredditsViewSchema,
    PostViewSchema,
    SubredditViewSchema,
    UserProfileViewSchema,
    UserViewSchema,
)

user = Blueprint("user", __name__)


@user.route("/profile", methods=["GET"])
@jwt_required(fresh=True)
def get_profile():
    if current_user:
        profile = User.query.filter_by(username=current_user.username).first()

        if profile:
            profile_schema = UserViewSchema.from_orm(profile)
            subreddits_schema = AllSubredditsViewSchema(
                subreddits=[
                    SubredditViewSchema(
                        name=subreddit.name,
                        description=subreddit.description,
                        id=subreddit.id,
                        user=profile_schema,
                        created_on=subreddit.created_on,
                    )
                    for subreddit in Subreddit.query.filter(
                        Subreddit.created_by == profile.id
                    ).all()
                ]
            )

            posts_schema = AllPostsViewSchema(
                posts=[
                    PostViewSchema(
                        id=post.id,
                        subreddit_id=post.belongs_to,
                        title=post.title,
                        text=post.text,
                        votes=post.votes,
                        user=profile_schema,
                        comments=None,
                        created_on=post.created_on,
                    )
                    for post in Post.query.filter(Post.created_by == profile.id).all()
                ]
            )

            response = UserProfileViewSchema(
                id=profile.id,
                username=profile.username,
                cake_day=profile.cake_day,
                email=profile.email,
                subreddits=subreddits_schema,
                posts=posts_schema,
            ).dict(exclude_unset=True, exclude_none=True)

            return response, HTTPStatus.OK

    return jsonify(message="User not Found"), HTTPStatus.NOT_FOUND
