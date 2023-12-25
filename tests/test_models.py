from tafakari.tafakari.models.comments import Comments
from tafakari.tafakari.models.posts import Post
from tafakari.tafakari.models.subreddit import Subreddit
from tafakari.tafakari.models.users import User, check_password


def test_user_model() -> None:
    """Tests the User Model"""
    user = User.create(
        username="Tester",
        email="tester@email.co.ke",
        password="password",
        is_admin=False,
    )

    assert user.username == "Tester"
    assert user.email == "tester@email.co.ke"
    assert check_password(user.password, "password")

    user.delete()


def test_subreddit_model() -> None:
    """Tests the Subreddit Model"""
    subreddit = Subreddit.create(
        name="Subreddit Test", description="Subreddit Test", created_by=1
    )

    assert subreddit.name == "Subreddit Test"
    assert subreddit.description == "Subreddit Test"
    assert subreddit.created_by == 1

    subreddit.delete()


def test_post_model(mock_subreddit: dict) -> None:
    """Tests the Post Model

    Args:
        mock_subreddit (dict): Dummy Subreddit Record
    """
    post = Post.create(
        title="Post Test", text="Post Test", votes=10, created_by=1, belongs_to=1
    )

    assert post.title == "Post Test"
    assert post.text == "Post Test"
    assert post.votes == 10
    assert post.created_by == 1
    assert post.belongs_to == 1

    post.delete()


def test_comments_model(mock_post: dict) -> None:
    """Tests the Comment Model

    Args:
        mock_post (dict): Dummy Post Record
    """
    comment = Comments.create(comment="Post Comment", votes=-100, user_id=1, post_id=1)

    assert comment.user_id == 1
    assert comment.post_id == 1
    assert comment.votes == -100
    assert comment.comment == "Post Comment"

    comment.delete()
