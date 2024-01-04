import pendulum

from ...configs import configs
from ..controllers.schemas import (
    AllCommentsViewSchema,
    CommentViewSchema,
    UserViewSchema,
)
from ..database import db
from ..extensions import cache
from . import CRUDMixin


class Comments(db.Model, CRUDMixin):
    """
    Represents a comment
    """

    __tablename__ = "comments"

    comment = db.Column(db.String(1000), nullable=False, unique=False)
    votes = db.Column(db.Integer, default=1, nullable=False)
    created_on = db.Column(
        db.DateTime(timezone=True), default=pendulum.now, nullable=False
    )

    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey("comments.id"), nullable=True)

    # Relationships
    user = db.relationship("User", back_populates="comments", uselist=False)
    post = db.relationship("Post", back_populates="comments", uselist=False)

    # Self-Referential Relationships
    children = db.relationship("Comments", back_populates="parent", uselist=True)
    parent = db.relationship(
        "Comments", back_populates="children", remote_side="Comments.id"
    )

    def __repr__(self) -> str:
        return f"<Comment: {self.comment}>"

    @cache.memoize(timeout=configs.CACHE_DEFAULT_TIMEOUT)
    def get_parent_comment(self) -> CommentViewSchema | None:
        """Returns the parent comment of a reply comment

        Returns:
            CommentViewSchema | None: The Parent Comment as a serialisable schema. Returns None if comment is the parent
        """
        if self.parent:
            parent_comment = self.parent
            parent = CommentViewSchema(
                id=parent_comment.id,
                comment=parent_comment.comment,
                votes=parent_comment.votes,
                created_on=parent_comment.created_on,
                user=UserViewSchema.from_orm(parent_comment.user),
                post_id=parent_comment.post_id,
                parent_id=parent_comment.parent_id,
            )
            return parent

        return None

    @cache.memoize(timeout=configs.CACHE_DEFAULT_TIMEOUT)
    def get_direct_comment_replies(self) -> AllCommentsViewSchema:
        """Returns all children comments of this comment

        Returns:
            list: All Child Comments
        """
        all_comments = []

        for comment in self.children:
            all_comments.append(
                CommentViewSchema(
                    comment=comment.comment,
                    id=comment.id,
                    votes=comment.votes,
                    created_on=comment.created_on,
                    user=UserViewSchema.from_orm(comment.user),
                    post_id=comment.post_id,
                    parent_id=comment.parent_id,
                )
            )

        return AllCommentsViewSchema(comments=all_comments)
