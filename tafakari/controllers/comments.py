from http import HTTPStatus

import pendulum
from flask import Blueprint, Response, jsonify
from flask_jwt_extended import current_user, jwt_required
from flask_pydantic import validate
from sqlalchemy import and_

from ..extensions import cache, limiter
from ..models.comments import Comments
from ..models.posts import Post
from .schemas import CommentRequestSchema, CommentViewSchema, UserViewSchema

comments = Blueprint("comments", __name__)


@comments.route("/posts/<int:post_id>/comments", methods=["POST"])
@limiter.limit("100/hour")
@validate(body=CommentRequestSchema)
@jwt_required(fresh=True)
def add_comment(body: CommentRequestSchema, post_id: int) -> tuple[Response, int]:
    """Adds a Comment to a Post

    Args:
        body (CommentRequestSchema): The Comment Request Schema
        post_id (int): The Post Id parsed from URL

    Returns:
        tuple[Response, int]: The Response Object and Status Code
    """
    post = Post.query.filter(Post.id == post_id).first()

    if post and current_user:
        comment = Comments.create(
            comment=body.comment, user_id=current_user.id, post_id=post_id
        )

        cache.delete(f"post_{post_id}")
        cache.delete(f"{current_user.username}_profile")
        return (
            jsonify(
                message=comment.comment,
                creator=comment.user_id,
                created_on=comment.created_on,
            ),
            HTTPStatus.CREATED,
        )

    return jsonify(message="No such post exists"), HTTPStatus.NOT_FOUND


@comments.route("/posts/<int:post_id>/comments/<int:comment_id>", methods=["PUT"])
@limiter.limit("5/hour")
@validate(body=CommentRequestSchema)
@jwt_required(fresh=True)
def update_comment(
    body: CommentRequestSchema, post_id: int, comment_id: int
) -> tuple[Response, int]:
    """Update a Comment in a Post

    Args:
        body (CommentRequestSchema): The Request Body from Client
        post_id (int): Id of Post comment belongs to
        comment_id (int): Id of the comment to update

    Returns:
        tuple[Response, int]: Response Object and Status Code
    """
    post = Post.get_by_id(post_id)

    if post and current_user:
        comment: Comments = Comments.query.filter(
            and_(Comments.post_id == post_id, Comments.user_id == current_user.id)
        ).first()

        if comment:
            updated_comment: Comments = comment.update(
                comment=body.comment, modified_on=pendulum.now()
            )

            response = CommentViewSchema(
                comment=updated_comment.comment,
                id=updated_comment.id,
                votes=updated_comment.votes,
                created_on=updated_comment.created_on,
                user=UserViewSchema.from_orm(current_user),
                post_id=post_id,
            ).dict()

            cache.delete(f"post_{post_id}")
            cache.delete(f"{current_user.username}_profile")
            return jsonify(response), HTTPStatus.ACCEPTED

        return (
            jsonify(message="You can't edit a comment you did not create"),
            HTTPStatus.FORBIDDEN,
        )

    return (
        jsonify(message="You are not allowed to access this resource"),
        HTTPStatus.FORBIDDEN,
    )


@comments.route("/posts/<int:post_id>/comments/<int:comment_id>", methods=["DELETE"])
@limiter.limit("10/day")
@jwt_required(fresh=True)
def delete_a_comment(post_id: int, comment_id: int) -> tuple[Response, int]:
    """Deletes a Comment in a Post

    Args:
        post_id (int): The Post Id parsed from URL
        comment_id (int): The Comment Id parsed from URL

    Returns:
        tuple[Response, int]: The Response Object and Status Code
    """
    post = Post.query.filter(Post.id == post_id).first()

    if post and current_user:
        comment = Comments.query.filter(
            and_(Comments.id == comment_id, Comments.user_id == current_user.id)
        ).first()

        if comment:
            comment.delete()

            cache.delete(f"post_{post_id}")
            cache.delete(f"{current_user.username}_profile")
            return jsonify(message="Comment deleted successfully"), HTTPStatus.OK

        return (
            jsonify(message="The comment you selected does not exist"),
            HTTPStatus.NOT_FOUND,
        )

    return jsonify(message="The post cannot be found"), HTTPStatus.NOT_FOUND


@comments.route(
    "/posts/<int:post_id>/comments/<int:comment_id>/upvote", methods=["GET"]
)
@limiter.exempt
@jwt_required(fresh=True)
def upvote_a_post_comment(post_id: int, comment_id: int) -> tuple[Response, int]:
    """Upvote a Comment in a Post

    Args:
        post_id (int): The Post Id parsed from URL
        comment_id (int): The Comment Id parsed from URL

    Returns:
        tuple[Response, int]: The Response Object and Status Code
    """
    post = Post.query.filter(Post.id == post_id).first()

    if post and current_user:
        comment = Comments.query.filter(
            and_(Comments.post_id == post_id, Comments.id == comment_id)
        ).first()

        if comment:
            comment.update(votes=comment.votes + 1)

            comment.save()

            cache.delete(f"post_{post_id}")
            cache.delete(f"{current_user.username}_profile")
            return jsonify(message="Up-voted Successfully"), HTTPStatus.ACCEPTED

        return (
            jsonify(message="The comment you selected does not exist"),
            HTTPStatus.NOT_FOUND,
        )

    return jsonify(message="The post cannot be found"), HTTPStatus.NOT_FOUND


@comments.route(
    "/posts/<int:post_id>/comments/<int:comment_id>/downvote", methods=["GET"]
)
@limiter.exempt
@jwt_required(fresh=True)
def downvote_a_post_comment(post_id: int, comment_id: int) -> tuple[Response, int]:
    """Downvote a Comment in a Post

    Args:
        post_id (int): The Post Id parsed from URL
        comment_id (int): The comment Id parsed from URL

    Returns:
        tuple[Response, int]: The Response Object and Status Code
    """
    post = Post.query.filter(Post.id == post_id).first()

    if post and current_user:
        comment = Comments.query.filter(
            and_(Comments.post_id == post_id, Comments.id == comment_id)
        ).first()

        if comment and current_user:
            comment.update(votes=comment.votes - 1)

            comment.save()

            cache.delete(f"post_{post_id}")
            cache.delete(f"{current_user.username}_profile")
            return jsonify(message="Down-voted Successfully"), HTTPStatus.ACCEPTED

        return (
            jsonify(message="The comment you selected does not exist"),
            HTTPStatus.NOT_FOUND,
        )

    return jsonify(message="The post cannot be found"), HTTPStatus.NOT_FOUND
