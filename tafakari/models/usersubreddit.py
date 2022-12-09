import pendulum

from ..database import db

user_subreddit_junction_table = db.Table(
    "user_subreddit",
    db.Column("user_id", db.ForeignKey("user.id"), primary_key=True),
    db.Column("subreddit_id", db.ForeignKey("subreddit.id"), primary_key=True),
    db.Column("date_of_joining", db.DateTime, default=pendulum.now, nullable=False)
)
