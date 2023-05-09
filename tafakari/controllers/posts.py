from http import HTTPStatus

import pendulum
from flask import Blueprint, jsonify
from flask_jwt_extended import current_user, jwt_required
from flask_pydantic import validate

from .schemas import PostsRequestSchema
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
            belongs_to=subreddit.id
        )

        post_to_create.save()

        return jsonify({
            "message": f"Post {body.title} created",
            "timestamp": pendulum.now()
        }), HTTPStatus.CREATED

    elif not current_user:
        return {
            "message": "No user with such an Id exists."
        }, HTTPStatus.FORBIDDEN

    elif not subreddit:
        return {
            "message": "Cannot create a post to a non-existent subreddit."
        }, HTTPStatus.NOT_FOUND
    return {
        "message": "Fatal Failure"
    }, HTTPStatus.EXPECTATION_FAILED


@posts.route("/get/subreddit/<subreddit_id>/get/post", methods=["POST"])
def get_all_posts(subreddit_id: int):
    all_posts = Post.query.filter_by(belongs_to=subreddit_id).all()
    subreddit = Subreddit.get_by_id(subreddit_id)

    if all_posts:
        return {
            "subreddit": subreddit.name,
            "Posts": [
                {
                    "title": post.title,
                    "text": post.text,
                    "votes": post.votes,
                    "created": post.created_on,
                    "created_by": post.created_by
                } for post in all_posts
            ]
        }, HTTPStatus.OK

    return {
        "message": "No posts yet"
    }, HTTPStatus.NOT_FOUND


@posts.route("/get/posts/<post_id>", methods=["GET"])
def get_post_by_id(post_id: int):
    post = Post.get_by_id(post_id)

    if post:
        return jsonify(
            post=post.title,
            text=post.text,
            votes=post.votes,
            created_on=post.created_on,
            created_by=post.created_by
        ), HTTPStatus.OK

    return jsonify(
        message="No post yet"
    ), HTTPStatus.NOT_FOUND


@posts.route("/get/post/<post_id>/upvote", methods=["GET"])
@jwt_required(fresh=True)
def upvote_a_post(post_id: int):
    post = Post.get_by_id(post_id)

    if post and current_user:
        post.update(votes=post.votes + 1)

        post.save()

        return {
            "message": "Up-voted Successfully"
        }, HTTPStatus.ACCEPTED

    return {
        "message": "The post you selected does not exist"
    }, HTTPStatus.NOT_FOUND


@posts.route("/get/post/<post_id>/downvote", methods=["GET"])
@jwt_required(fresh=True)
def downvote_a_post(post_id: int):
    post = Post.get_by_id(post_id)

    if post and current_user:
        post.update(votes=post.votes - 1)

        post.save()

        return {
            "message": "Down-voted Successfully"
        }, HTTPStatus.ACCEPTED

    return {
        "message": "The post you selected does not exist"
    }, HTTPStatus.NOT_FOUND
