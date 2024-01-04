import pendulum

from ..database import db
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
