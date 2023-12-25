import pendulum

from . import CRUDMixin
from ..database import db


class Post(db.Model, CRUDMixin):
    __tablename__ = "post"
    title = db.Column(db.String(200), nullable=False, unique=False)
    text = db.Column(db.String(1000), nullable=True, unique=False)
    votes = db.Column(db.Integer, nullable=False, default=1)
    created_on = db.Column(db.DateTime(timezone=True), default=pendulum.now, nullable=False)

    # Foreign Keys
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    belongs_to = db.Column(db.Integer, db.ForeignKey("subreddit.id"), nullable=False)

    # Relationships
    user = db.relationship("User", back_populates="posts", uselist=False)
    subreddit = db.relationship("Subreddit", back_populates="posts", uselist=False)
    comments = db.relationship("Comments", back_populates="post")

    def __repr__(self) -> str:
        return f"<Post: {self.title}>"
