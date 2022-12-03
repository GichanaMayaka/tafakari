import pendulum

from ..database import db


class Post(db.Model):
    __tablename__ = "post"
    id = db.Column(db.Integer, primary_key=True)
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

    def __init__(self, title: str, text: str) -> None:
        self.title = title
        self.text = text

    def __repr__(self) -> str:
        return f"<Post: {self.title}>"
