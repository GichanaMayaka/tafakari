import pendulum

from ..database import db


class Comments(db.Model):
    """
        Represents a comment
    """
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(1000), nullable=False, unique=False)
    votes = db.Column(db.Integer, default=1, nullable=False)
    created_on = db.Column(db.DateTime, default=pendulum.now, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), primary_key=True)

    def __init__(self, comment: str) -> None:
        self.comment = comment
