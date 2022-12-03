import pendulum

from ..database import db
from .usersubreddit import user_subreddit_junction_table


class Subreddit(db.Model):
    """
        Represents a Subreddit - a collection of posts, and users...
        basically a community
    """
    __tablename__ = "subreddit"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    description = db.Column(db.String(240), nullable=False, unique=True)
    created_on = db.Column(db.DateTime, default=pendulum.now, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    post_id = db.relationship(
        "Post",
        lazy="select",
        backref=db.backref(
            "subreddit",
            lazy="joined"
        )
    )
    users = db.relationship(
        "User",
        secondary=user_subreddit_junction_table,
        back_populates="subreddits"
    )

    def __init__(self, name: str, description: str) -> None:
        self.name = name
        self.description = description

    def __repr__(self) -> str:
        return f"<Subreddit: {self.name}>"
