from http import HTTPStatus

from flask.testing import FlaskClient

from ..tafakari.models.posts import Post
from .test_subreddits import set_authorization_token


def test_create_a_post_valid(
    client_app: FlaskClient, login_test_user: str, create_mock_subreddit: dict
) -> None:
    mock_post_body = {
        "subreddit_id": 1,
        "title": "JMW Turner",
        "text": "I love JMW Turner's watercolour paintings",
    }

    with client_app as test_client:
        response = test_client.post(
            "/posts",
            json=mock_post_body,
            headers=set_authorization_token(login_test_user),
        )

    assert response.status_code == HTTPStatus.CREATED


def test_create_a_post_to_non_existent_subreddit(
    client_app: FlaskClient,
    login_test_user: str,
) -> None:
    mock_post_body = {
        "subreddit_id": 0,
        "title": "JMW Turner",
        "text": "I love JMW Turner's watercolour paintings",
    }

    with client_app as test_client:
        response = test_client.post(
            "/posts",
            json=mock_post_body,
            headers=set_authorization_token(login_test_user),
        )

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_create_a_post_with_invalid_access_token(
    client_app: FlaskClient, login_test_user: str, create_mock_subreddit
) -> None:
    mock_post_body = {
        "subreddit_id": 1,
        "title": "JMW Turner",
        "text": "I love JMW Turner's watercolour paintings",
    }

    with client_app as test_client:
        response = test_client.post(
            "/posts",
            json=mock_post_body,
            headers=set_authorization_token("abcdefg"),
        )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_create_a_post_with_no_access_token(
    client_app: FlaskClient, create_mock_subreddit
) -> None:
    mock_post_body = {
        "subreddit_id": 1,
        "title": "JMW Turner",
        "text": "I love JMW Turner's watercolour paintings",
    }

    with client_app as test_client:
        response = test_client.post(
            "/posts",
            json=mock_post_body,
        )

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_create_a_post_incomplete_form_values(
    client_app: FlaskClient, login_test_user: str, create_mock_subreddit: dict
) -> None:
    mock_post_body = {
        "subreddit_id": 1,
        "title": "JMW Turner",
    }

    with client_app as test_client:
        response = test_client.post(
            "/posts",
            json=mock_post_body,
            headers=set_authorization_token(login_test_user),
        )

    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_update_a_post(
    client_app: FlaskClient, login_test_user: str, create_mock_subreddit: dict
) -> None:
    mock_post_body = {
        "subreddit_id": 1,
        "title": "JMW Turner",
        "text": "I love JMW Turner's watercolour paintings so much!",
    }

    with client_app as test_client:
        response = test_client.put(
            "/posts/1",
            json=mock_post_body,
            headers=set_authorization_token(login_test_user),
        )

    assert response.status_code == HTTPStatus.ACCEPTED

    post: Post = Post.query.filter_by(text=mock_post_body["text"]).first()

    assert post is not None
    assert post.text == mock_post_body["text"]


def test_update_a_post_to_non_existent_subreddit(
    client_app: FlaskClient,
    login_test_user: str,
) -> None:
    mock_post_body = {
        "subreddit_id": 0,
        "title": "JMW Turner",
        "text": "I love JMW Turner's watercolour paintings so much!",
    }

    with client_app as test_client:
        response = test_client.put(
            "/posts/1",
            json=mock_post_body,
            headers=set_authorization_token(login_test_user),
        )

    assert response.status_code == HTTPStatus.NOT_FOUND

    post: Post = Post.query.filter_by(text=mock_post_body["text"]).first()

    assert post is None


def test_update_a_post_invalid_token(
    client_app: FlaskClient, login_test_user: str, create_mock_subreddit: dict
) -> None:
    mock_post_body = {
        "subreddit_id": 1,
        "title": "JMW Turner",
        "text": "I love JMW Turner's watercolour paintings so much!",
    }

    with client_app as test_client:
        response = test_client.put(
            "/posts/1",
            json=mock_post_body,
            headers=set_authorization_token("abcde12345"),
        )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    post: Post = Post.query.filter_by(text=mock_post_body["text"]).first()

    assert post is None


def test_update_a_post_no_access_token(
    client_app: FlaskClient, create_mock_subreddit: dict
) -> None:
    mock_post_body = {
        "subreddit_id": 1,
        "title": "JMW Turner",
        "text": "I love JMW Turner's watercolour paintings so much!",
    }

    with client_app as test_client:
        response = test_client.put(
            "/posts/1",
            json=mock_post_body,
        )

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    post: Post = Post.query.filter_by(text=mock_post_body["text"]).first()

    assert post is None


def test_update_a_post_incomplete_form(
    client_app: FlaskClient, create_mock_subreddit: dict, login_test_user: str
) -> None:
    mock_post_body = {
        "subreddit_id": 1,
        "text": "I love JMW Turner's watercolour paintings so much!",
    }

    with client_app as test_client:
        response = test_client.put(
            "/posts/1",
            json=mock_post_body,
            headers=set_authorization_token(login_test_user),
        )

    assert response.status_code == HTTPStatus.BAD_REQUEST

    post: Post = Post.query.filter_by(text=mock_post_body["text"]).first()

    assert post is None


def test_get_all_posts(
    client_app: FlaskClient, create_mock_subreddit: dict, create_mock_post: dict
) -> None:
    with client_app as test_client:
        response = test_client.get("/posts")

    assert response.status_code == HTTPStatus.OK
    assert len(response.json["posts"]) > 0
    assert isinstance(response.json["posts"][0], dict)


def test_get_post_by_id(
    client_app: FlaskClient, create_mock_subreddit: dict, create_mock_post: dict
) -> None:
    post_id = 1
    with client_app as test_client:
        response = test_client.get(f"/posts/{post_id}")

    json_response = response.json
    assert response.status_code == HTTPStatus.OK
    assert json_response["id"] == post_id


def test_get_non_existent_post_by_id(
    client_app: FlaskClient, create_mock_subreddit: dict, create_mock_post: dict
) -> None:
    post_id = 0

    with client_app as test_client:
        response = test_client.get(f"/posts/{post_id}")

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_upvote_a_post(
    client_app: FlaskClient,
    login_test_user: str,
    create_mock_subreddit: dict,
    create_mock_post: dict,
) -> None:
    post_id = 1
    with client_app as test_client:
        response = test_client.get(
            f"/posts/{post_id}/upvote", headers=set_authorization_token(login_test_user)
        )

    assert response.status_code == HTTPStatus.ACCEPTED

    post: Post = Post.get_by_id(post_id)

    assert post is not None
    assert post.votes == 2


def test_upvote_a_non_existent_post(
    client_app: FlaskClient,
    login_test_user: str,
    create_mock_subreddit: dict,
    create_mock_post: dict,
) -> None:
    post_id = 0
    with client_app as test_client:
        response = test_client.get(
            f"/posts/{post_id}/upvote", headers=set_authorization_token(login_test_user)
        )

    assert response.status_code == HTTPStatus.NOT_FOUND

    post: Post = Post.get_by_id(post_id)

    assert post is None


def test_upvote_a_post_invalid_access_token(
    client_app: FlaskClient,
    create_mock_subreddit: dict,
    create_mock_post: dict,
) -> None:
    post_id = 1
    with client_app as test_client:
        response = test_client.get(
            f"/posts/{post_id}/upvote", headers=set_authorization_token("abcde12345")
        )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    post: Post = Post.get_by_id(post_id)

    assert post is not None
    assert post.votes == 1


def test_upvote_a_post_no_access_token(client_app: FlaskClient) -> None:
    post_id = 1
    with client_app as test_client:
        response = test_client.get(f"/posts/{post_id}/upvote")

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_downvote_a_post(
    client_app: FlaskClient,
    login_test_user: str,
    create_mock_subreddit: dict,
    create_mock_post: dict,
) -> None:
    post_id = 1
    with client_app as test_client:
        response = test_client.get(
            f"/posts/{post_id}/downvote",
            headers=set_authorization_token(login_test_user),
        )

    assert response.status_code == HTTPStatus.ACCEPTED

    post: Post = Post.get_by_id(post_id)

    assert post is not None
    assert post.votes == 0


def test_downvote_a_non_existent_post(
    client_app: FlaskClient,
    login_test_user: str,
    create_mock_subreddit: dict,
    create_mock_post: dict,
) -> None:
    post_id = 0
    with client_app as test_client:
        response = test_client.get(
            f"/posts/{post_id}/downvote",
            headers=set_authorization_token(login_test_user),
        )

    assert response.status_code == HTTPStatus.NOT_FOUND

    post: Post = Post.get_by_id(post_id)

    assert post is None


def test_downote_a_post_invalid_access_token(
    client_app: FlaskClient,
    create_mock_subreddit: dict,
    create_mock_post: dict,
) -> None:
    post_id = 1
    with client_app as test_client:
        response = test_client.get(
            f"/posts/{post_id}/downvote", headers=set_authorization_token("abcde12345")
        )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    post: Post = Post.get_by_id(post_id)

    assert post is not None
    assert post.votes == 1


def test_downvote_a_post_no_access_token(client_app: FlaskClient) -> None:
    post_id = 1
    with client_app as test_client:
        response = test_client.get(f"/posts/{post_id}/downvote")

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_delete_a_post(
    client_app: FlaskClient,
    login_test_user: str,
    create_mock_subreddit: dict,
    create_mock_post: dict,
) -> None:
    post_id = 1
    with client_app as test_client:
        response = test_client.delete(
            f"/posts/{post_id}", headers=set_authorization_token(login_test_user)
        )

    assert response.status_code == HTTPStatus.ACCEPTED

    post = Post.get_by_id(post_id)

    assert post is None


def test_delete_a_non_existent_post(
    client_app: FlaskClient, login_test_user: str
) -> None:
    post_id = 0
    with client_app as test_client:
        response = test_client.delete(
            f"/posts/{post_id}", headers=set_authorization_token(login_test_user)
        )

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_delete_a_post_invalid_access_token(
    client_app: FlaskClient,
    create_mock_subreddit: dict,
    create_mock_post: dict,
) -> None:
    post_id = 1
    with client_app as test_client:
        response = test_client.delete(
            f"/posts/{post_id}", headers=set_authorization_token("12345")
        )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_delete_a_post_no_access_token(
    client_app: FlaskClient,
    create_mock_subreddit: dict,
    create_mock_post: dict,
) -> None:
    post_id = 1
    with client_app as test_client:
        response = test_client.delete(f"/posts/{post_id}")

    assert response.status_code == HTTPStatus.UNAUTHORIZED
