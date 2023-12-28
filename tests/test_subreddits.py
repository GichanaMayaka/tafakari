from http import HTTPStatus


def set_authorization_token(token: str) -> dict:
    """Sets valid access token headers

    Args:
        token (str): Access Token value to set

    Returns:
        dict: Authentication Header
    """
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def test_get_all_subreddits_valid(client_app, mock_subreddit):
    subreddit_response = mock_subreddit

    with client_app as test_client:
        response = test_client.get("/subreddits")

        assert response.status_code == HTTPStatus.OK


def test_create_a_subreddit_unauthorised(client_app):
    mock_subreddit = dict(name="Test Subreddit", description="This is a test Subreddit")

    with client_app as test_client:
        response = test_client.post(
            "/subreddits",
            json=mock_subreddit,
            headers=set_authorization_token("invalid_token"),
        )

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_create_a_subreddit_valid(client_app, login_test_user):
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


def test_create_a_subreddit_duplicated(client_app, login_test_user, mock_subreddit):
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
