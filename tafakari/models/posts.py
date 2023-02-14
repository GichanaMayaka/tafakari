import pendulum

from . import CRUDMixin
from ..database import db


class Post(db.Model, CRUDMixin):
    __tablename__ = "post"
    title = db.Column(db.String(200), nullable=False, unique=False)
    text = db.Column(db.String(1000), nullable=True, unique=False)
    votes = db.Column(db.Integer, nullable=False, default=1)
    created_on = db.Column(db.DateTime, default=pendulum.now, nullable=False)
    created_by = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )
    belongs_to = db.Column(
        db.Integer,
        db.ForeignKey("subreddit.id"),
        nullable=False
    )
    comments = db.relationship(
        "Comments",
        lazy="select",
        backref=db.backref(
            "post",
            lazy="joined"
        )
    )

    def __repr__(self) -> str:
        return f"<Post: {self.title}>"
