import pendulum
from flask import Blueprint
from flask_pydantic import validate

from .schemas import PostsRequestSchema, PostsBaseModel
from ..database import db
from ..models.posts import Post
from ..models.subreddit import Subreddit
from ..models.users import User

posts = Blueprint("post", __name__, template_folder="templates")


@posts.route("/create/post", methods=["POST"])
@validate(body=PostsRequestSchema)
def create_subreddit_post(body: PostsRequestSchema):
    user = User.query.filter_by(id=body.metadata.user_id).first()
    subreddit = Subreddit.query.filter_by(id=body.metadata.subreddit_id).first()

    if user and subreddit:
        post_to_create = Post(
            title=body.title,
            text=body.text
        )
        post_to_create.created_by = user.id
        post_to_create.belongs_to = subreddit.id

        db.session.add(post_to_create)
        db.session.commit()

        return {
            "message": f"Post {body.title} created",
            "timestamp": pendulum.now()
        }, 201

    elif not user:
        return {
            "message": "No user with such an Id exists."
        }, 403

    elif not subreddit:
        return {
            "message": "Cannot create a post to a non-existent subreddit."
        }, 404
    return {
        "message": "Fatal Failure"
    }, 417


@posts.route("/get/posts", methods=["POST"])
@validate(body=PostsBaseModel)
def get_all_posts(body: PostsBaseModel):
    all_posts = Post.query.filter_by(belongs_to=body.subreddit_id).all()
    subreddit = Subreddit.query.filter_by(id=body.subreddit_id).first()

    if all_posts:
        return {
            "subreddit": subreddit.name,
            "Posts": [{"title": post.title, "text": post.text} for post in all_posts]
        }, 200

    return {
        "message": "No posts yet"
    }, 404


@posts.route("/get/post/<post_id>/upvote", methods=["GET"])
def upvote_a_post(post_id: int):
    post = Post.query.filter_by(id=post_id).first()

    if post:
        post.votes += 1

        db.session.add(post)
        db.session.commit()

        return {
            "message": "Up-voted Successfully"
        }, 202

    return {
        "message": "The post you selected does not exist"
    }, 406


@posts.route("/get/post/<post_id>/downvote", methods=["GET"])
def downvote_a_post(post_id: int):
    post = Post.query.filter_by(id=post_id).first()

    if post:
        post.votes -= 1

        db.session.add(post)
        db.session.commit()

        return {
            "message": "Down-voted Successfully"
        }, 202

    return {
        "message": "The post you selected does not exist"
    }, 406
