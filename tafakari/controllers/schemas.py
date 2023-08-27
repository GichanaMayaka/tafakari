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


class CommentRequestSchema(BaseTafakariSchema):
    """Comment Request Schema"""

    comment: str


class CommentViewSchema(CommentRequestSchema):
    """Comment Response Schema"""

    id: int
    votes: int
    created_on: datetime.datetime
    user: UserViewSchema


class CreatePostRequestSchema(BaseTafakariSchema):
    """Create Post Request Schema"""

    subreddit_id: int
    title: str
    text: str


class PostViewSchema(BaseTafakariSchema):
    """Post Response Schema"""

    id: int
    subreddit_id: int
    title: str
    text: str
    votes: int
    user: Optional[UserViewSchema]
    comments: Optional[list[CommentViewSchema]]


class AllPostsViewSchema(BaseTafakariSchema):
    """All Posts Response Schema"""

    posts: Optional[list[PostViewSchema]]


class CreateSubredditRequestSchema(BaseTafakariSchema):
    """Create Subreddit Request Schema"""

    name: str
    description: str


class SubredditViewSchema(CreateSubredditRequestSchema):
    """Subreddit Response Schema"""

    id: int
    user: Optional[UserViewSchema]
    created_on: datetime.datetime


class AllSubredditsViewSchema(BaseTafakariSchema):
    """All Subreddits Response Schema"""

    subreddits: list[SubredditViewSchema]


class UserProfileViewSchema(UserViewSchema):
    cake_day: datetime.datetime
    email: str
    subreddits: Optional[AllSubredditsViewSchema]
    posts: Optional[AllPostsViewSchema]
