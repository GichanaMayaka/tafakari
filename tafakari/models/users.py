import uuid

import pendulum

from . import CRUDMixin
from .usersubreddit import user_subreddit_junction_table
from ..database import db
from ..extensions import bcrypt


class User(db.Model, CRUDMixin):
    """
    Represents a user
    """

    __tablename__ = "user"

    external_id = db.Column(db.String, nullable=False, index=True, default=uuid.uuid4)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    cake_day = db.Column(
        db.DateTime, default=pendulum.now, nullable=False
    )  # date of joining
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    # Relationships
    posts = db.relationship("Post", back_populates="user")
    subreddits = db.relationship(
        "Subreddit", secondary=user_subreddit_junction_table, back_populates="user"
    )
    comments = db.relationship("Comments", back_populates="user")

    def __init__(
        self, username: str, email: str, password: str, is_admin: bool = False
    ) -> None:
        self.username = username
        self.email = email
        self.password = hash_password(password)
        self.is_admin = is_admin

    def __repr__(self) -> str:
        return f"<User {self.username}>"


def hash_password(password: str) -> bytes:
    return bcrypt.generate_password_hash(password).decode("utf-8")


def check_password(hashed_pwd: str, pwd: str) -> bool:
    return bcrypt.check_password_hash(hashed_pwd, pwd)
