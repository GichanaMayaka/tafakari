import pendulum

from ...configs import configs
from ..controllers.schemas import UserViewSchema
from ..database import db
from ..extensions import cache
from . import CRUDMixin
from .usersubreddit import user_subreddit_junction_table


class Subreddit(db.Model, CRUDMixin):
    """
    Represents a Subreddit - a collection of posts, and users...
    basically a community
    """

    __tablename__ = "subreddit"
    name = db.Column(db.String(120), nullable=False, unique=True)
    description = db.Column(db.String(240), nullable=False, unique=False)
    created_on = db.Column(
        db.DateTime(timezone=True), default=pendulum.now, nullable=False
    )

    # Foreign Keys
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    # Relationships
    posts = db.relationship(
        "Post", back_populates="subreddit", uselist=False, cascade="all, delete-orphan"
    )
    user = db.relationship(
        "User", secondary=user_subreddit_junction_table, back_populates="subreddits"
    )

    def __repr__(self) -> str:
        return f"<Subreddit: {self.name}>"

    @cache.memoize(timeout=configs.CACHE_DEFAULT_TIMEOUT)
    def get_members(self) -> list[UserViewSchema]:
        """Returns all Members in a Subreddit

        Returns:
            list[UserViewSchema]: All Users that are members of this Subreddit
        """
        all_members = []
        for member in self.user:
            all_members.append(UserViewSchema.from_orm(member))

        return all_members
