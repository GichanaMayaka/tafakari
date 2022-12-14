from http import HTTPStatus

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, current_user
from flask_pydantic import validate
from sqlalchemy import and_

from .schemas import CommentRequestSchema
from .. import Post, Comments

comments = Blueprint(
    "comments",
    __name__
)


@comments.route("/get/posts/<post_id>/create/comment", methods=["GET", "POST"])
@validate(body=CommentRequestSchema)
@jwt_required(fresh=True)
def add_comment(body: CommentRequestSchema, post_id: int):
    post: Post = Post.get_by_id(post_id)

    if post and current_user:
        c: Comments = Comments.create(
            comment=body.comment,
            user_id=current_user.id,
            post_id=post_id
        )
        c.save()
        return jsonify(
            message=c.comment,
            creator=c.user_id,
            created_on=c.created_on
        ), HTTPStatus.CREATED

    if not post:
        return jsonify(
            message="No such post"
        ), HTTPStatus.NOT_FOUND

    return jsonify(
        message="No such post exists"
    ), HTTPStatus.NOT_FOUND


@comments.route("/get/posts/<post_id>/delete/comment/<comment_id>", methods=["DELETE"])
@jwt_required(fresh=True)
def delete_a_comment(post_id: int, comment_id: int):
    post: Post = Post.get_by_id(post_id)

    if post and current_user:
        comment: Comments = Comments.query.filter(
            and_(
                Comments.id == comment_id,
                Comments.user_id == current_user.id
            )
        ).first()

        if comment:
            comment.delete()

            return jsonify(
                message="Comment deleted successfully"
            ), HTTPStatus.ACCEPTED

        elif not comment:
            return jsonify(
                message="No such comment"
            ), HTTPStatus.NOT_FOUND

    return jsonify(
        message="No such post exists"
    ), HTTPStatus.NOT_FOUND
