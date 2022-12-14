import pendulum
from sqlalchemy_serializer import SerializerMixin

from . import CRUDMixin
from ..database import db


class Comments(db.Model, CRUDMixin, SerializerMixin):
    """
        Represents a comment
    """
    __tablename__ = "comments"
    comment = db.Column(db.String(1000), nullable=False, unique=False)
    votes = db.Column(db.Integer, default=1, nullable=False)
    created_on = db.Column(db.DateTime, default=pendulum.now, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), primary_key=True)

    def __repr__(self) -> str:
        return f"<Comment: {self.comment}>"
