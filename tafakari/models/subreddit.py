import pendulum

from . import CRUDMixin
from .usersubreddit import user_subreddit_junction_table
from ..database import db


class Subreddit(db.Model, CRUDMixin):
    """
    Represents a Subreddit - a collection of posts, and users...
    basically a community
    """

    __tablename__ = "subreddit"
    name = db.Column(db.String(120), nullable=False, unique=True)
    description = db.Column(db.String(240), nullable=False, unique=False)
    created_on = db.Column(db.DateTime(timezone=True), default=pendulum.now, nullable=False)

    # Foreign Keys
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    # Relationships
    posts = db.relationship("Post", back_populates="subreddit", uselist=False)
    user = db.relationship(
        "User", secondary=user_subreddit_junction_table, back_populates="subreddits"
    )

    def __repr__(self) -> str:
        return f"<Subreddit: {self.name}>"
