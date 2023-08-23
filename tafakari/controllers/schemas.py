import datetime
from typing import Optional

from pydantic import BaseModel


class BaseTafakariSchema(BaseModel):
    """Base Model Schema"""

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class UserViewSchema(BaseTafakariSchema):
    """User Response Schema"""

    id: int
    username: str


class UserRequestSchema(BaseTafakariSchema):
    """User Request Schema"""

    username: str
    email: str
    password: str
    is_admin: Optional[bool]


class CreateSubredditRequestSchema(BaseTafakariSchema):
    """Create Subreddit Request Schema"""

    name: str
    description: str


class SubredditViewSchema(CreateSubredditRequestSchema):
    """Subreddit Response Schema"""

    id: int
    user: UserViewSchema
    created_on: datetime.datetime


class AllSubredditsViewSchema(BaseTafakariSchema):
    """All Subreddits Response Schema"""

    subreddits: list[SubredditViewSchema]


class CommentRequestSchema(BaseTafakariSchema):
    """Comment Request Schema"""

    comment: str


class CommentViewSchema(CommentRequestSchema):
    """Comment Response Schema"""

    comment_id: int
    comment_votes: int
    created_on: datetime.datetime


class CreatePostRequestSchema(BaseTafakariSchema):
    """Create Post Request Schema"""

    title: str
    text: str


class PostViewSchema(CreatePostRequestSchema):
    """Post Response Schema"""

    id: int
    votes: int
    username: str  # username name
    subreddit_name: str  # Subreddit name
    comments: Optional[list[CommentViewSchema]]


class AllPosts(BaseTafakariSchema):
    """All Posts Response Schema"""

    posts: Optional[list[PostViewSchema]]


class AllPostsInSubredditSchema(AllPosts):
    subreddit: str


class UserProfileViewSchema(BaseTafakariSchema):
    external_id: str
    username: str
    cake_day: datetime.datetime
    email: str
    subreddits: Optional[list[SubredditViewSchema]]
    post: Optional[list[PostViewSchema]]
