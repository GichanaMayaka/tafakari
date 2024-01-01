from http import HTTPStatus

from flask import Blueprint, Response, jsonify
from flask_jwt_extended import current_user, jwt_required

from ..extensions import cache
from ..models.comments import Comments
from ..models.posts import Post
from ..models.subreddit import Subreddit
from ..models.users import User
from .schemas import (
    AllCommentsViewSchema,
    AllPostsViewSchema,
    AllSubredditsViewSchema,
    CommentViewSchema,
    PostViewSchema,
    SubredditViewSchema,
    UserProfileViewSchema,
    UserViewSchema,
)

user = Blueprint("user", __name__)


@user.route("/profile", methods=["GET"])
@jwt_required(fresh=True)
def get_profile() -> tuple[Response | str, int]:
    """Get current signed in user's profile

    Returns:
        tuple[Response | str, int]: Response Object and Status Code
    """
    cached_data = cache.get(f"{current_user.username}_profile")

    if not cached_data:
        if current_user:
            profile: User = User.query.filter_by(username=current_user.username).first()

            if profile:
                profile_schema = UserViewSchema.from_orm(profile)

                created_subreddits = [
                    SubredditViewSchema(
                        name=subreddit.name,
                        description=subreddit.description,
                        id=subreddit.id,
                        members=subreddit.get_members(),
                        created_on=subreddit.created_on,
                    )
                    for subreddit in Subreddit.query.filter(
                        Subreddit.created_by == profile.id
                    ).all()
                ]

                joined_subs = profile.get_joined_sureddits()

                if joined_subs:
                    created_subreddits.extend(joined_subs)

                all_subreddits = AllSubredditsViewSchema(
                    subreddits=created_subreddits
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
                        for post in Post.query.filter(
                            Post.created_by == profile.id
                        ).all()
                    ]
                )

                comments_schema = AllCommentsViewSchema(
                    comments=[
                        CommentViewSchema(
                            comment=comment.comment,
                            id=comment.id,
                            votes=comment.votes,
                            created_on=comment.created_on,
                            user=profile_schema,
                            post_id=comment.post_id,
                        )
                        for comment in Comments.query.filter(
                            Comments.user_id == profile.id
                        )
                    ]
                )

                response = UserProfileViewSchema(
                    id=profile.id,
                    username=profile.username,
                    cake_day=profile.cake_day,
                    email=profile.email,
                    subreddits=all_subreddits,
                    posts=posts_schema,
                    comments=comments_schema,
                ).dict(exclude_unset=True, exclude_none=True)

                cache.set(f"{current_user.username}_profile", response)
                return jsonify(response), HTTPStatus.OK

        return jsonify(message="User not Found"), HTTPStatus.NOT_FOUND

    return jsonify(cached_data), HTTPStatus.OK
