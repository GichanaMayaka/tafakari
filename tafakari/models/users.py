import pendulum

from ..database import db
from ..extensions import bcrypt
from .usersubreddit import user_subreddit_junction_table


class User(db.Model):
    """
        Represents a user
    """
    # TODO: Add karma functionality
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    cake_day = db.Column(db.DateTime, default=pendulum.now, nullable=False)  # date of joining
    post = db.relationship(
        "Post",
        lazy="select",
        backref=db.backref(
            "user",
            lazy="joined"
        )
    )
    subreddits = db.relationship(
        "Subreddit",
        secondary=user_subreddit_junction_table,
        back_populates="users"
    )
    comments = db.relationship(
        "Comments",
        lazy="select",
        backref=db.backref(
            "user",
            lazy="joined"
        )
    )

    def __init__(self, username: str, email: str, password: str) -> None:
        self.username = username
        self.email = email
        self.password = self.hash_password(password)

    def hash_password(self, password: str) -> bytes:
        return bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password) -> bool:
        return bcrypt.check_password_hash(self.password, password)

    def __repr__(self) -> str:
        return f"<User {self.username}>"
