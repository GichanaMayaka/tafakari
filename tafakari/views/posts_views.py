from http import HTTPStatus

import pendulum
from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from flask_pydantic import validate

from .schemas import PostsRequestSchema, PostsBaseModel
from ..database import db
from ..models.posts import Post
from ..models.subreddit import Subreddit

posts = Blueprint("post", __name__, template_folder="templates")


@posts.route("/create/post", methods=["POST"])
@validate(body=PostsRequestSchema)
@login_required
def create_subreddit_post(body: PostsRequestSchema):
    subreddit = Subreddit.get_by_id(body.metadata.subreddit_id)

    if current_user and subreddit:
        post_to_create = Post.create(
            title=body.title,
            text=body.text,
            created_by=current_user.id,
            belongs_to=subreddit.id
        )

        db.session.add(post_to_create)
        db.session.commit()

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


@posts.route("/get/posts", methods=["POST"])
@validate(body=PostsBaseModel)
def get_all_posts(body: PostsBaseModel):
    all_posts = Post.query.filter_by(belongs_to=body.subreddit_id).all()
    subreddit = Subreddit.get_by_id(body.subreddit_id)

    if all_posts:
        return {
            "subreddit": subreddit.name,
            "Posts": [{"title": post.title, "text": post.text} for post in all_posts]
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
            created_on=post.created_on,
            created_by=post.created_by
        ), HTTPStatus.OK

    return jsonify(
        message="No post yet"
    ), HTTPStatus.NOT_FOUND


@posts.route("/get/post/<post_id>/upvote", methods=["GET"])
@login_required
def upvote_a_post(post_id: int):
    post = Post.get_by_id(post_id)

    if post and current_user:
        post.votes += 1

        db.session.add(post)
        db.session.commit()

        return {
            "message": "Up-voted Successfully"
        }, HTTPStatus.ACCEPTED

    return {
        "message": "The post you selected does not exist"
    }, HTTPStatus.NOT_ACCEPTABLE


@posts.route("/get/post/<post_id>/downvote", methods=["GET"])
@login_required
def downvote_a_post(post_id: int):
    post = Post.get_by_id(post_id)

    if post and current_user:
        post.votes -= 1

        db.session.add(post)
        db.session.commit()

        return {
            "message": "Down-voted Successfully"
        }, HTTPStatus.ACCEPTED

    return {
        "message": "The post you selected does not exist"
    }, HTTPStatus.NOT_ACCEPTABLE
