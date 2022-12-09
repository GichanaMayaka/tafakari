from typing import Optional

from pydantic import BaseModel


class BaseTafakariSchema(BaseModel):
    class Config:
        orm_mode = True


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
    metadata: PostsBaseModel
    title: str
    text: str
