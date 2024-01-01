from http import HTTPStatus

import pendulum
from flask import Blueprint, Response, jsonify
from flask_jwt_extended import current_user, jwt_required
from flask_pydantic import validate
from sqlalchemy import and_

from tafakari.configs import configs

from ..extensions import cache, limiter
from ..models.comments import Comments
from ..models.posts import Post
from ..models.subreddit import Subreddit
from ..models.users import User
from .schemas import (
    AllPostsViewSchema,
    CommentViewSchema,
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
        body (CreatePostRequestSchema): Request Schema

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

        cache.set(
            f"post_{new_post.id}",
            created_post,
            timeout=configs.CACHE_DEFAULT_TIMEOUT,
        )
        cache.delete(f"{current_user.username}_profile")
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


@posts.route("/posts", methods=["GET"])
@limiter.limit("1000/day")
def get_all_posts() -> tuple[Response | str, int]:
    """Get all posts irregardless of subreddit

    Returns:
        tuple[Response | str, int]: Response Object and Status Code
    """
    cached_data = cache.get("all_posts")

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

            cache.set("all_posts", response, timeout=configs.CACHE_DEFAULT_TIMEOUT)

            return (
                jsonify(response),
                HTTPStatus.OK,
            )

        return jsonify(message="No Post Found"), HTTPStatus.NOT_FOUND

    return cached_data, HTTPStatus.OK


@posts.route("/subreddits/<int:subreddit_id>/posts", methods=["GET"])
@limiter.limit("1000/day")
def get_all_posts_in_subreddit(subreddit_id: int) -> tuple[Response | str, int]:
    """Get all the posts in a particular subreddit identified by its Id

    Args:
        subreddit_id (int): Subreddit Id parsed from URL

    Returns:
        tuple[Response | str, int]: Response Object and Status Code
    """
    cached_data = cache.get(f"all_posts_in_subreddit_{subreddit_id}")

    if not cached_data:
        subreddit = Subreddit.get_by_id(subreddit_id)

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

                cache.set(
                    f"all_posts_in_subreddit_{subreddit_id}",
                    response,
                    timeout=configs.CACHE_DEFAULT_TIMEOUT,
                )
                return (
                    jsonify(response),
                    HTTPStatus.OK,
                )

            return jsonify(message="No Post Found"), HTTPStatus.NOT_FOUND

        return jsonify(message="Subreddit Not Found"), HTTPStatus.NOT_FOUND

    return cached_data, HTTPStatus.OK


@posts.route("/posts/<int:post_id>", methods=["GET"])
@limiter.limit("1000/day")
def get_post_by_id(post_id: int) -> tuple[Response | str, int]:
    """Gets posts by specific Id

    Args:
        post_id (int): Post Id parsed from URL

    Returns:
        tuple[Response | str, int]: Response Object and Status Code
    """
    cached_data = cache.get(f"post_{post_id}")

    if not cached_data:
        post = Post.get_by_id(post_id)

        if post:
            post_creator = User.get_by_id(post.created_by)
            subreddit = Subreddit.get_by_id(post.belongs_to)
            all_post_comments = Comments.query.filter(
                and_(Comments.post_id == post.id)
            ).all()

            if post_creator:
                comments_collection = []

                for comment in all_post_comments:
                    comment_creator = User.get_by_id(comment.user_id)
                    comment_creator_schema = UserViewSchema.from_orm(comment_creator)

                    comment_schema = CommentViewSchema(
                        id=comment.id,
                        votes=comment.votes,
                        created_on=comment.created_on,
                        user=comment_creator_schema,
                        comment=comment.comment,
                        post_id=post.id,
                    )
                    comments_collection.append(comment_schema)

                post_creator_schema = UserViewSchema.from_orm(post_creator)

                post_response = PostViewSchema(
                    id=post.id,
                    subreddit_id=subreddit.id,
                    title=post.title,
                    text=post.text,
                    votes=post.votes,
                    user=post_creator_schema,
                    comments=comments_collection,
                    created_on=post.created_on,
                ).dict(exclude_none=True)

                cache.set(
                    f"post_{post_id}",
                    post_response,
                    timeout=configs.CACHE_DEFAULT_TIMEOUT,
                )
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
    post = Post.get_by_id(post_id)

    if post and current_user:
        post.update(votes=post.votes + 1)

        cache.delete("all_posts")
        cache.delete(f"post_{post_id}")
        cache.delete(f"{current_user.username}_profile")
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
    post = Post.get_by_id(post_id)

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
