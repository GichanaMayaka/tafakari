from typing import Optional

from pydantic import BaseModel


class BaseTafakariModel(BaseModel):
    class Config:
        orm_mode = True


class UserRequestSchema(BaseTafakariModel):
    username: str
    email: str
    password: str


class CreateSubredditPostSchema(BaseTafakariModel):
    name: str
    description: str


class PostsBaseModel(BaseTafakariModel):
    subreddit_id: int
    user_id: int


class PostsRequestSchema(BaseTafakariModel):
    metadata: PostsBaseModel
    title: str
    text: str
