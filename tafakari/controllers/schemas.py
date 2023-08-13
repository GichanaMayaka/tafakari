import datetime
from typing import Optional

from pydantic import BaseModel


class BaseTafakariSchema(BaseModel):
    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class UserRequestSchema(BaseTafakariSchema):
    username: str
    email: str
    password: str
    is_admin: Optional[bool]


class CreateSubredditPostSchema(BaseTafakariSchema):
    name: str
    description: str


class PostsBaseModel(BaseTafakariSchema):
    subreddit_id: int
    user_id: int


class PostsRequestSchema(BaseTafakariSchema):
    title: str
    text: str


class CommentRequestSchema(BaseTafakariSchema):
    comment: str


class CommentResponseSchema(BaseTafakariSchema):
    comment_id: int
    comment: str
    comment_votes: int
    created_on: datetime.datetime


class PostResponseSchema(BaseTafakariSchema):
    id: int
    title: str
    text: str
    votes: int
    username: str  # username name
    subreddit_name: str  # Subreddit name
    comments: Optional[list[CommentResponseSchema]]


class SubredditResponseSchema(BaseTafakariSchema):
    id: int
    name: str
    description: str
    created_by: str
    created_on: datetime.datetime


class SubredditViewSchema(BaseTafakariSchema):
    name: str
    description: str
    created_by: str
    created_on: datetime.datetime


class AllPosts(BaseTafakariSchema):
    posts: Optional[list[PostResponseSchema]]


class AllPostsInSubredditSchema(BaseTafakariSchema):
    subreddit: str
    posts: list[PostResponseSchema]


class UserProfileViewSchema(BaseTafakariSchema):
    external_id: str
    username: str
    cake_day: datetime.datetime
    email: str
    subreddits: Optional[list[SubredditResponseSchema]]
    post: Optional[list[PostResponseSchema]]
