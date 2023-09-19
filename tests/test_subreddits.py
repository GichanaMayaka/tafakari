from http import HTTPStatus


def test_create_a_subreddit_valid(client_app, login_test_user):
    mock_subreddit = dict(name="Test Subreddit", description="This is a test Subreddit")
    headers = {
        "Authorization": f"Bearer {login_test_user.json['access_token']}",
        "Content-Type": "application/json",
    }

    with client_app as test_client:
        response = test_client.post("/subreddits", json=mock_subreddit, headers=headers)

        assert response.status_code == HTTPStatus.OK
        assert response.json == dict(message="created")
