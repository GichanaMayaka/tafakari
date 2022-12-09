import uuid

import pendulum
from sqlalchemy_serializer import SerializerMixin
from flask_login import UserMixin

from ..database import CRUDMixin, db
from ..extensions import bcrypt
from .usersubreddit import user_subreddit_junction_table


class User(db.Model, CRUDMixin, SerializerMixin, UserMixin):
    """
        Represents a user
    """
    # TODO: Add karma functionality
    __tablename__ = "user"
    external_id = db.Column(
        db.String,
        nullable=False,
        index=True,
        default=uuid.uuid4
    )
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    cake_day = db.Column(db.DateTime, default=pendulum.now,
                         nullable=False)  # date of joining
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
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

    def __init__(self, username: str, email: str, password: str, is_admin: bool = False) -> None:
        self.username = username
        self.email = email
        self.password = hash_password(password)
        self.is_admin = is_admin

    def __repr__(self) -> str:
        return f"<User {self.username}>"


def hash_password(password: str) -> bytes:
    return bcrypt.generate_password_hash(password).decode("utf-8")


def check_password(hashed_pwd, pwd) -> bool:
    return bcrypt.check_password_hash(hashed_pwd, pwd)
