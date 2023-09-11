from http import HTTPStatus

import pendulum
from flask import Blueprint, jsonify
from flask_jwt_extended import current_user, jwt_required
from flask_pydantic import validate
from sqlalchemy import and_

from ...configs import configs
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
def create_subreddit_post(body: CreatePostRequestSchema):
    """Create a post in a subreddit"""
    subreddit = Subreddit.get_by_id(body.subreddit_id)

    if current_user and subreddit:
        Post.create(
            title=body.title,
            text=body.text,
            created_by=current_user.id,
            belongs_to=subreddit.id,
        )

        return (
            jsonify(message=f"Post {body.title} created", timestamp=pendulum.now()),
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
@cache.cached(timeout=configs.CACHE_DEFAULT_TIMEOUT)
def get_all_posts():
    """Get all posts regardless of subreddit"""
    all_posts = Post.query.all()

    all_posts_response = []
    if all_posts:
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

        return (
            jsonify(
                AllPostsViewSchema(posts=all_posts_response).dict(exclude_none=True)
            ),
            HTTPStatus.OK,
        )

    return jsonify(message="No Post Found"), HTTPStatus.NOT_FOUND


@posts.route("/subreddits/<int:subreddit_id>/posts", methods=["GET"])
@limiter.limit("1000/day")
@cache.cached(timeout=configs.CACHE_DEFAULT_TIMEOUT)
def get_all_posts_in_subreddit(subreddit_id: int):
    """Get all the posts in a particular subreddit identified by its Id"""
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

            return (
                AllPostsViewSchema(posts=all_posts_response).dict(exclude_none=True),
                HTTPStatus.OK,
            )

        return jsonify(message="No Post Found"), HTTPStatus.NOT_FOUND

    return jsonify(message="Subreddit Not Found"), HTTPStatus.NOT_FOUND


@posts.route("/posts/<int:post_id>", methods=["GET"])
@limiter.limit("1000/day")
def get_post_by_id(post_id: int):
    post = Post.get_by_id(post_id)

    if post:
        post_creator = User.get_by_id(post.created_by)
        subreddit = Subreddit.get_by_id(post.belongs_to)
        all_post_comments = Comments.query.filter(
            and_(Comments.user_id == post.created_by, Comments.post_id == post.id)
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

            return post_response, HTTPStatus.OK

    return jsonify(message="Post Not Found"), HTTPStatus.NOT_FOUND


@posts.route("/posts/<int:post_id>/upvote", methods=["GET"])
@limiter.exempt
@jwt_required(fresh=True)
def upvote_a_post(post_id: int):
    # TODO: Make up-votes unique per user
    post = Post.get_by_id(post_id).first()

    if post and current_user:
        post.update(votes=post.votes + 1)

        return jsonify(message="Up-voted Successfully"), HTTPStatus.ACCEPTED

    return {"message": "The post you selected does not exist"}, HTTPStatus.NOT_FOUND


@posts.route("/posts/<int:post_id>/downvote", methods=["GET"])
@limiter.exempt
@jwt_required(fresh=True)
def downvote_a_post(post_id: int):
    # TODO: Make down-votes unique per user
    post = Post.get_by_id(post_id)

    if post and current_user:
        post.update(votes=post.votes - 1)

        return jsonify(message="Down-voted Successfully"), HTTPStatus.ACCEPTED

    return jsonify(message="The post you selected does not exist"), HTTPStatus.NOT_FOUND
