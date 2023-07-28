from http import HTTPStatus

import pendulum
from flask import Blueprint, jsonify
from flask_jwt_extended import current_user, jwt_required
from flask_pydantic import validate
from sqlalchemy import and_

from .schemas import PostsRequestSchema, AllPostsInSubredditSchema
from ..models.posts import Post
from ..models.subreddit import Subreddit

posts = Blueprint("post", __name__, template_folder="templates")


@posts.route("/get/subreddit/<subreddit_id>/create/post", methods=["POST"])
@validate(body=PostsRequestSchema)
@jwt_required(fresh=True)
def create_subreddit_post(body: PostsRequestSchema, subreddit_id: int):
    subreddit = Subreddit.get_by_id(subreddit_id)

    if current_user and subreddit:
        post_to_create = Post.create(
            title=body.title,
            text=body.text,
            created_by=current_user.id,
            belongs_to=subreddit.id,
        )

        return (
            jsonify(message=f"Post {body.title} created", timestamp=pendulum.now()),
            HTTPStatus.CREATED,
        )

    return jsonify(message="Fatal Failure"), HTTPStatus.EXPECTATION_FAILED


@posts.route("/get/subreddit/<subreddit_id>/get/post", methods=["GET"])
def get_all_posts_in_subreddit(subreddit_id: int):
    all_posts = Post.query.filter_by(belongs_to=subreddit_id).all()
    subreddit = Subreddit.get_by_id(subreddit_id)

    if all_posts:
        return (
            AllPostsInSubredditSchema(subreddit=subreddit.name, posts=all_posts).dict(),
            HTTPStatus.OK,
        )

    return jsonify(message="No Posts yet"), HTTPStatus.NOT_FOUND


@posts.route("/get/subreddit/<subreddit_id>/get/post/<post_id>", methods=["GET"])
def get_post_by_id(subreddit_id: int, post_id: int):
    post = Post.query.filter(
        and_(Post.belongs_to == subreddit_id, Post.id == post_id)
    ).first()

    if post:
        return (
            jsonify(
                post=post.title,
                text=post.text,
                votes=post.votes,
                created_on=post.created_on,
                created_by=post.created_by,
            ),
            HTTPStatus.OK,
        )

    return jsonify(message="No post yet"), HTTPStatus.NOT_FOUND


@posts.route("/get/subreddit/<subreddit_id>/get/post/<post_id>/upvote", methods=["GET"])
@jwt_required(fresh=True)
def upvote_a_post(subreddit_id: int, post_id: int):
    # TODO: Make upvotes/downvotes unique per user
    post = Post.query.filter(
        and_(Post.id == post_id, Post.belongs_to == subreddit_id)
    ).first()

    if post and current_user:
        post.update(votes=post.votes + 1)

        post.save()

        return jsonify(message="Up-voted Successfully"), HTTPStatus.ACCEPTED

    return {"message": "The post you selected does not exist"}, HTTPStatus.NOT_FOUND


@posts.route(
    "/get/subreddit/<subreddit_id>/get/post/<post_id>/downvote", methods=["GET"]
)
@jwt_required(fresh=True)
def downvote_a_post(subreddit_id: int, post_id: int):
    post = Post.get_by_id(post_id)

    if post and current_user:
        post.update(votes=post.votes - 1)

        post.save()

        return jsonify(message="Down-voted Successfully"), HTTPStatus.ACCEPTED

    return jsonify(message="The post you selected does not exist"), HTTPStatus.NOT_FOUND
