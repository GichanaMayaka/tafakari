import pendulum

from ...configs import configs
from ..controllers.schemas import (
    CommentViewSchema,
    UserViewSchema,
    AllCommentsViewSchema,
)
from ..database import db
from ..extensions import cache
from . import CRUDMixin


class Post(db.Model, CRUDMixin):
    """Represents a Post

    Args:
        db (Model): SQLAlchemy db object
        CRUDMixin (CRUDMixin): Mixins

    Returns:
        Post: Represents a Post
    """

    __tablename__ = "post"
    title = db.Column(db.String(200), nullable=False, unique=False)
    text = db.Column(db.String(1000), nullable=True, unique=False)
    votes = db.Column(db.Integer, nullable=False, default=1)
    created_on = db.Column(
        db.DateTime(timezone=True), default=pendulum.now, nullable=False
    )

    # Foreign Keys
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    belongs_to = db.Column(db.Integer, db.ForeignKey("subreddit.id"), nullable=False)

    # Relationships
    user = db.relationship("User", back_populates="posts", uselist=False)
    subreddit = db.relationship("Subreddit", back_populates="posts", uselist=False)
    comments = db.relationship(
        "Comments", back_populates="post", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Post: {self.title}>"

    @cache.memoize(timeout=configs.CACHE_DEFAULT_TIMEOUT)
    def get_all_post_comments(self) -> AllCommentsViewSchema:
        """Returns all Comments in this Post

        Returns:
            list[CommentViewSchema]: All Comments in this Post
        """
        all_comments = []
        for comment in self.comments:
            all_comments.append(
                CommentViewSchema(
                    comment=comment.comment,
                    id=comment.id,
                    votes=comment.votes,
                    created_on=comment.created_on,
                    post_id=comment.post_id,
                    user=UserViewSchema.from_orm(comment.user),
                    parent_id=comment.parent_id,
                )
            )

        return AllCommentsViewSchema(comments=all_comments)
