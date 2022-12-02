import pendulum

from ..database import db


class Subreddit(db.Model):
    __tablename__ = "subreddit"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    description = db.Column(db.String(240), nullable=False, unique=True)
    votes = db.Column(db.Integer, default=1, nullable=False)
    created_on = db.Column(db.DateTime, default=pendulum.now, nullable=False)
    created_by = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    post = db.relationship(
        "Post",
        lazy="select",
        backref=db.backref(
            "subreddit",
            lazy="joined"
        )
    )

    def __init__(self, name: str, description: str) -> None:
        self.name = name
        self.description = description

    def __repr__(self) -> str:
        return f"<Subreddit: {self.name}>"
