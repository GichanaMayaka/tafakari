import pendulum

from ..database import db
from ..extensions import bcrypt


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    # Change column type to Binary-type column
    password = db.Column(db.LargeBinary, nullable=False)
    cake_day = db.Column(db.DateTime, default=pendulum.now, nullable=False)
    subreddit = db.relationship(
        "Subreddit",
        lazy="select",
        backref=db.backref(
            "user",
            lazy="joined"
        )
    )
    post = db.relationship(
        "Post",
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
        return bcrypt.generate_password_hash(password)

    def check_password(self, password) -> bool:
        return bcrypt.check_password_hash(self.password, password)

    def __repr__(self) -> str:
        return f"<User {self.username}>"
