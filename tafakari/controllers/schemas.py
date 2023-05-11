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


class CommentReponseSchema(BaseTafakariSchema):
    comment: str
    votes: int
    created_on: datetime.datetime


class PostResponseSchema(BaseTafakariSchema):
    title: str
    text: str
    votes: int
    comments: Optional[list[CommentReponseSchema]]


class SubredditResponseSchema(BaseTafakariSchema):
    id: int
    name: str
    description: str
    created_by: str
    created_on: datetime.datetime


class UserProfileViewSchema(BaseTafakariSchema):
    external_id: str
    username: str
    cake_day: datetime.datetime
    email: str
    subreddits: Optional[list[SubredditResponseSchema]]
    post: Optional[list[PostResponseSchema]]


class SubredditViewSchema(BaseTafakariSchema):
    name: str
    description: str
    created_by: str
    created_on: datetime.datetime
