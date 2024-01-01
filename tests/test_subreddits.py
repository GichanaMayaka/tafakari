from http import HTTPStatus

from flask.testing import FlaskClient


def set_authorization_token(token: str) -> dict[str, str]:
    """Sets valid access token headers for the current test user

    Args:
        token (str): Access Token value to set

    Returns:
        dict[str, str]: Authentication Header
    """
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def test_get_all_subreddits_valid(client_app: FlaskClient, create_mock_subreddit):
    subreddit_response = create_mock_subreddit

    with client_app as test_client:
        response = test_client.get("/subreddits")

        assert response.status_code == HTTPStatus.OK


def test_create_a_subreddit_unauthorised(client_app: FlaskClient):
    mock_subreddit = dict(name="Test Subreddit", description="This is a test Subreddit")

    with client_app as test_client:
        response = test_client.post(
            "/subreddits",
            json=mock_subreddit,
            headers=set_authorization_token("invalid_token"),
        )

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_create_a_subreddit_valid(client_app: FlaskClient, login_test_user):
    mock_subreddit = dict(
        name="Another Test Subreddit", description="This is another test Subreddit"
    )

    with client_app as test_client:
        response = test_client.post(
            "/subreddits",
            json=mock_subreddit,
            headers=set_authorization_token(login_test_user),
        )

        assert response.status_code == HTTPStatus.CREATED
        assert response.json == dict(message="created")


def test_create_a_subreddit_duplicated(
    client_app: FlaskClient, login_test_user, create_mock_subreddit
):
    duplicated_subreddit = dict(
        name="Test Subreddit", description="This is a test Subreddit"
    )

    with client_app as test_client:
        response = test_client.post(
            "/subreddits",
            json=duplicated_subreddit,
            headers=set_authorization_token(login_test_user),
        )

        assert response.status_code == HTTPStatus.CONFLICT
        assert response.json == dict(
            message=f"A subreddit with the title: {duplicated_subreddit['name']}, already exists"
        )


def test_get_subreddit_by_id_valid(
    client_app: FlaskClient, create_mock_subreddit: dict
) -> None:
    with client_app as test_client:
        response = test_client.get("/subreddits/1")

    assert response.status_code == HTTPStatus.OK


def test_get_all_subreddits_invalid(client_app: FlaskClient) -> None:
    with client_app as test_client:
        response = test_client.get("/subreddits/0")

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json == dict(message="No Subreddit Found")


def test_join_a_joined_sureddit(
    client_app: FlaskClient, login_test_user: str, create_mock_subreddit: dict
) -> None:
    with client_app as test_client:
        response = test_client.get(
            "/join/subreddits/1", headers=set_authorization_token(login_test_user)
        )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json == dict(message="You have already joined.")


def test_join_a_non_existent_sureddit(
    client_app: FlaskClient, login_test_user: str
) -> None:
    with client_app as test_client:
        response = test_client.get(
            "/join/subreddits/0", headers=set_authorization_token(login_test_user)
        )

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_join_a_subreddit_not_authorised(
    client_app: FlaskClient, login_test_user: str, create_mock_subreddit: dict
) -> None:
    with client_app as test_client:
        response = test_client.get(
            "/join/subreddits/1", headers=set_authorization_token("abcde")
        )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_delete_a_subreddit(
    client_app: FlaskClient, create_mock_subreddit: dict, login_test_user: str
) -> None:
    with client_app as test_client:
        response = test_client.delete(
            "/subreddits/1", headers=set_authorization_token(login_test_user)
        )

    assert response.status_code == HTTPStatus.ACCEPTED


def test_delete_a_subreddit_not_authorised(
    client_app: FlaskClient, create_mock_subreddit: dict
) -> None:
    with client_app as test_client:
        response = test_client.delete(
            "/subreddits/1", headers=set_authorization_token("abcde")
        )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
