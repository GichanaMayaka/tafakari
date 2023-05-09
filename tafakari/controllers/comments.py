from http import HTTPStatus

from flask import Blueprint, jsonify
from flask_jwt_extended import current_user, jwt_required
from flask_pydantic import validate
from sqlalchemy import and_

from .schemas import CommentRequestSchema
from ..models.comments import Comments
from ..models.posts import Post

comments = Blueprint("comments", __name__)


@comments.route("/get/post/<post_id>/create/comment", methods=["POST"])
@validate(body=CommentRequestSchema)
@jwt_required(fresh=True)
def add_comment(body: CommentRequestSchema, post_id: int):
    post: Post = Post.get_by_id(post_id)

    if post and current_user:
        comment: Comments = Comments.create(
            comment=body.comment,
            user_id=current_user.id,
            post_id=post_id
        )
        comment.save()
        return jsonify(
            message=comment.comment,
            creator=comment.user_id,
            created_on=comment.created_on
        ), HTTPStatus.CREATED

    if not post:
        return jsonify(
            message="No such post"
        ), HTTPStatus.NOT_FOUND

    return jsonify(
        message="No such post exists"
    ), HTTPStatus.NOT_FOUND


@comments.route("/get/post/<post_id>/delete/comment/<comment_id>", methods=["DELETE"])
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
                message="Cannot delete comment."
            ), HTTPStatus.NOT_FOUND

    return jsonify(
        message="No such post exists"
    ), HTTPStatus.NOT_FOUND


@comments.route("/get/post/<post_id>/upvote/comment/<comment_id>", methods=["GET"])
@jwt_required(fresh=True)
def upvote_a_post_comment(post_id: int, comment_id: int):
    comment = Comments.query.filter(
        and_(
            Comments.post_id == post_id,
            Comments.id == comment_id
        )
    ).first()

    if comment and current_user:
        comment.update(votes=comment.votes + 1)

        comment.save()

        return {
            "message": "Up-voted Successfully"
        }, HTTPStatus.ACCEPTED

    return {
        "message": "The comment you selected does not exist"
    }, HTTPStatus.NOT_FOUND


@comments.route("/get/post/<post_id>/downvote/comment/<comment_id>", methods=["GET"])
@jwt_required(fresh=True)
def downvote_a_post_comment(post_id: int, comment_id: int):
    comment = Comments.query.filter(
        and_(
            Comments.post_id == post_id,
            Comments.id == comment_id
        )
    ).first()

    if comment and current_user:
        comment.update(votes=comment.votes - 1)

        comment.save()

        return {
            "message": "Down-voted Successfully"
        }, HTTPStatus.ACCEPTED

    return {
        "message": "The comment you selected does not exist"
    }, HTTPStatus.NOT_FOUND
