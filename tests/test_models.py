import pytest

from ..tafakari.extensions import bcrypt
from ..tafakari.models.comments import Comments
from ..tafakari.models.posts import Post
from ..tafakari.models.subreddit import Subreddit
from ..tafakari.models.users import User


@pytest.fixture()
def user() -> User:
    yield User(
        username="Sir John Everett Millais",
        email="millais@art.com",
        password="password"
    )


@pytest.fixture()
def subreddit() -> Subreddit:
    yield Subreddit(
        name="The Pre-Raphaelite Brotherhood",
        description="Art Movements"
    )


@pytest.fixture()
def post() -> Post:
    yield Post(
        title="Ophelia",
        text="Painting by John Everett Millais"
    )


@pytest.fixture()
def comment() -> Comments:
    yield Comments(
        comment="Beautiful"
    )


def test_user(user) -> None:
    assert user.username == "Sir John Everett Millais"
    assert user.email == "millais@art.com"

    assert bcrypt.check_password_hash(user.password, "password")


def test_subreddits(subreddit) -> None:
    assert subreddit.name is "The Pre-Raphaelite Brotherhood"
    assert subreddit.description is "Art Movements"


def test_post(post) -> None:
    assert post.title is "Ophelia"
    assert post.text is "Painting by John Everett Millais"

    post.votes = 10

    assert post.votes == 10


def test_comments(comment) -> None:
    assert comment.comment == "Beautiful"
