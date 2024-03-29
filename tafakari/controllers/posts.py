from http import HTTPStatus

import pendulum
from flask import Blueprint, Response, jsonify
from flask_jwt_extended import current_user, jwt_required
from flask_pydantic import validate
from sqlalchemy import and_

from tafakari.configs import configs

from ..extensions import cache, limiter
from ..models.posts import Post
from ..models.subreddit import Subreddit
from ..models.users import User
from ..utils import CACHE_KEYS_REFERENCE, cache_invalidator, cache_setter
from .schemas import (
    AllPostsViewSchema,
    CreatePostRequestSchema,
    PostViewSchema,
    UserViewSchema,
)

posts = Blueprint("post", __name__)


@posts.route("/posts", methods=["POST"])
@limiter.limit("10/day")
@validate(body=CreatePostRequestSchema)
@jwt_required(fresh=True)
def create_subreddit_post(body: CreatePostRequestSchema) -> tuple[Response, int]:
    """Create a post in a subreddit

    Args:
        body (CreatePostRequestSchema): Request Body from Client

    Returns:
        tuple[Response, int]: Response Object and Status Code
    """
    subreddit = Subreddit.get_by_id(body.subreddit_id)

    if current_user and subreddit:
        new_post = Post.create(
            title=body.title,
            text=body.text,
            created_by=current_user.id,
            belongs_to=subreddit.id,
        )

        created_post = PostViewSchema(
            id=new_post.id,
            subreddit_id=new_post.belongs_to,
            title=new_post.title,
            text=new_post.text,
            votes=new_post.votes,
            created_on=new_post.created_on,
            user=UserViewSchema.from_orm(current_user),
            comments=None,
        ).dict()

        cache_setter(CACHE_KEYS_REFERENCE["POST_ID"](new_post.id), created_post)
        cache_invalidator(
            [
                CACHE_KEYS_REFERENCE["PROFILE"](current_user.username),
                CACHE_KEYS_REFERENCE["ALL_POSTS"],
                CACHE_KEYS_REFERENCE["ALL_POSTS_IN_SUBREDDIT"](subreddit.id),
            ]
        )
        return (
            jsonify(message=f"Post {new_post.title} created", timestamp=pendulum.now()),
            HTTPStatus.CREATED,
        )

    if not subreddit:
        return (
            jsonify(message="The subreddit you are trying to post to does not exist"),
            HTTPStatus.NOT_FOUND,
        )

    return (
        jsonify(message="Fatal Failure", current_user=current_user.username),
        HTTPStatus.EXPECTATION_FAILED,
    )


@posts.route("/posts/<int:post_id>", methods=["PUT"])
@limiter.limit("5/hour")
@validate(body=CreatePostRequestSchema)
@jwt_required(fresh=True)
def update_subreddit_post(
    body: CreatePostRequestSchema, post_id: int
) -> tuple[Response, int]:
    """Update/Edit a post in a subreddit

    Args:
        body (CreatePostRequestSchema): Request Body from Client

    Returns:
        tuple[Response, int]: Response Object and Status Code
    """
    subreddit = Subreddit.get_by_id(body.subreddit_id)

    if current_user and subreddit:
        post: Post = Post.query.filter(
            and_(
                Post.id == post_id,
                Post.created_by == current_user.id,
                Post.belongs_to == subreddit.id,
            )
        ).first()

        if post:
            updated_post: Post = post.update(
                title=body.title, text=body.text, modified_on=pendulum.now()
            )

            response = PostViewSchema(
                id=updated_post.id,
                subreddit_id=updated_post.belongs_to,
                title=updated_post.title,
                text=updated_post.text,
                votes=updated_post.votes,
                created_on=updated_post.created_on,
                user=UserViewSchema.from_orm(current_user),
                comments=post.get_all_post_comments(),
            ).dict()

            cache_setter(CACHE_KEYS_REFERENCE["POST_ID"](post_id), response)
            cache_invalidator(
                [
                    CACHE_KEYS_REFERENCE["ALL_POSTS"],
                    CACHE_KEYS_REFERENCE["PROFILE"](current_user.username),
                ]
            )
            return jsonify(response), HTTPStatus.ACCEPTED

        return (
            jsonify(message="You can't edit a Post you did not create"),
            HTTPStatus.FORBIDDEN,
        )

    return (
        jsonify(message="The requested resource was not found"),
        HTTPStatus.NOT_FOUND,
    )


@posts.route("/posts", methods=["GET"])
@limiter.limit("1000/day")
def get_all_posts() -> tuple[Response | str, int]:
    """Get all posts irregardless of subreddit

    Returns:
        tuple[Response | str, int]: Response Object and Status Code
    """
    cache_key = CACHE_KEYS_REFERENCE["ALL_POSTS"]
    cached_data = cache.get(cache_key)

    if not cached_data:
        all_posts = Post.query.all()

        if all_posts:
            all_posts_response = []

            for post in all_posts:
                creator = User.get_by_id(post.created_by)
                creator_schema = UserViewSchema.from_orm(creator)

                post = PostViewSchema(
                    subreddit_id=post.belongs_to,
                    title=post.title,
                    text=post.text,
                    id=post.id,
                    votes=post.votes,
                    user=creator_schema,
                    comments=None,
                    created_on=post.created_on,
                )

                all_posts_response.append(post)

            response = AllPostsViewSchema(posts=all_posts_response).dict(
                exclude_none=True
            )

            cache_setter(cache_key, response)

            return (
                jsonify(response),
                HTTPStatus.OK,
            )

        return jsonify(message="No Post Found"), HTTPStatus.NOT_FOUND

    return jsonify(cached_data), HTTPStatus.OK


@posts.route("/subreddits/<int:subreddit_id>/posts", methods=["GET"])
@limiter.limit("1000/day")
def get_all_posts_in_subreddit(subreddit_id: int) -> tuple[Response | str, int]:
    """Get all the posts in a particular subreddit identified by its Id

    Args:
        subreddit_id (int): Subreddit Id parsed from URL

    Returns:
        tuple[Response | str, int]: Response Object and Status Code
    """
    # TODO: Fix bug where controller fetches stale data after upvote action
    cache_key = CACHE_KEYS_REFERENCE["ALL_POSTS_IN_SUBREDDIT"](subreddit_id)
    cached_data = cache.get(cache_key)

    if not cached_data:
        subreddit: Subreddit = Subreddit.get_by_id(subreddit_id)

        if subreddit:
            all_posts = Post.query.filter_by(belongs_to=subreddit_id).all()

            all_posts_response = []
            if all_posts:
                for post in all_posts:
                    post_creator = User.get_by_id(post.created_by)
                    post_creator_schema = UserViewSchema.from_orm(post_creator)

                    post = PostViewSchema(
                        id=post.id,
                        subreddit_id=subreddit.id,
                        title=post.title,
                        text=post.text,
                        votes=post.votes,
                        user=post_creator_schema,
                        created_on=post.created_on,
                        comments=None,
                    )

                    all_posts_response.append(post)

                response = AllPostsViewSchema(posts=all_posts_response).dict(
                    exclude_none=True
                )

                cache_setter(cache_key, response)
                return (
                    jsonify(response),
                    HTTPStatus.OK,
                )

            return jsonify(message="No Post Found"), HTTPStatus.NOT_FOUND

        return jsonify(message="Subreddit Not Found"), HTTPStatus.NOT_FOUND

    return jsonify(cached_data), HTTPStatus.OK


@posts.route("/posts/<int:post_id>", methods=["GET"])
@limiter.limit("1000/day")
def get_post_by_id(post_id: int) -> tuple[Response | str, int]:
    """Gets posts by specific Id

    Args:
        post_id (int): Post Id parsed from URL

    Returns:
        tuple[Response | str, int]: Response Object and Status Code
    """
    cache_key = CACHE_KEYS_REFERENCE["POST_ID"](post_id)
    cached_data = cache.get(cache_key)

    if not cached_data:
        post: Post = Post.get_by_id(post_id)

        if post:
            post_creator = User.get_by_id(post.created_by)
            subreddit: Subreddit = Subreddit.get_by_id(post.belongs_to)
            all_post_comments = post.get_all_post_comments()

            if subreddit:
                post_creator_schema = UserViewSchema.from_orm(post_creator)

                post_response = PostViewSchema(
                    id=post.id,
                    subreddit_id=subreddit.id,
                    title=post.title,
                    text=post.text,
                    votes=post.votes,
                    user=post_creator_schema,
                    comments=all_post_comments,
                    created_on=post.created_on,
                ).dict()

                cache_setter(cache_key, post_response)
                return jsonify(post_response), HTTPStatus.OK

        return jsonify(message="Post Not Found"), HTTPStatus.NOT_FOUND

    return jsonify(cached_data), HTTPStatus.OK


@posts.route("/posts/<int:post_id>/upvote", methods=["GET"])
@limiter.exempt
@jwt_required(fresh=True)
def upvote_a_post(post_id: int) -> tuple[Response, int]:
    """Upvotes a Post

    Args:
        post_id (int): Post Id parsed from URL

    Returns:
        tuple[Response, int]: Response Object and Status Code
    """
    # TODO: Make up-votes unique per user
    post: Post = Post.get_by_id(post_id)

    if post and current_user:
        post.update(votes=post.votes + 1)

        cache.delete(CACHE_KEYS_REFERENCE["POST_ID"](post.id))
        cache_invalidator(
            [
                CACHE_KEYS_REFERENCE["ALL_POSTS"],
                CACHE_KEYS_REFERENCE["PROFILE"](current_user.username),
                CACHE_KEYS_REFERENCE["ALL_POSTS_IN_SUBREDDIT"](f"{post.belongs_to}"),
            ]
        )
        return jsonify(message="Up-voted Successfully"), HTTPStatus.ACCEPTED

    return jsonify(message="The post you selected does not exist"), HTTPStatus.NOT_FOUND


@posts.route("/posts/<int:post_id>/downvote", methods=["GET"])
@limiter.exempt
@jwt_required(fresh=True)
def downvote_a_post(post_id: int) -> tuple[Response, int]:
    """Downvotes a Post

    Args:
        post_id (int): Post Id parsed from URL

    Returns:
        tuple[Response, int]: Response Object and Status Code
    """
    # TODO: Make down-votes unique per user
    post: Post = Post.get_by_id(post_id)

    if post and current_user:
        post.update(votes=post.votes - 1)

        cache.delete("all_posts")
        cache.delete(f"post_{post_id}")
        cache.delete(f"{current_user.username}_profile")
        return jsonify(message="Down-voted Successfully"), HTTPStatus.ACCEPTED

    return jsonify(message="The post you selected does not exist"), HTTPStatus.NOT_FOUND


@posts.route("/posts/<int:post_id>", methods=["DELETE"])
@limiter.exempt
@jwt_required(fresh=True)
def delete_a_post(post_id: int) -> tuple[Response, int]:
    """Deletes a Post and its comments

    Args:
        post_id (int): Post Id parsed from URL

    Returns:
        tuple[Response, int]: The Response Oject and Status Code
    """
    post: Post = Post.get_by_id(post_id)

    if post and current_user:
        post.delete()

        cache.delete(f"post_{post_id}")
        cache.delete("all_posts")
        cache.delete(f"{current_user.username}_profile")
        return (
            jsonify(
                post=PostViewSchema(
                    id=post.id,
                    subreddit_id=post.belongs_to,
                    title=post.title,
                    text=post.text,
                    votes=post.votes,
                    created_on=post.created_on,
                    user=None,
                    comments=None,
                ).dict()
            ),
            HTTPStatus.ACCEPTED,
        )

    return (
        jsonify(message="The Post you are trying to delete is Not Found"),
        HTTPStatus.NOT_FOUND,
    )
