from http import HTTPStatus

from flask.testing import FlaskClient


def test_login_user_successful(register_test_user, client_app: FlaskClient) -> None:
    """Tests the Login User Controller

    Args:
        login_test_user (any): dummy test user record
        client_app (FlaskClient): _description_
    """
    with client_app as test_client:
        response = test_client.post(
            "/auth/login",
            json=dict(username="tester", email="tester@email.com", password="password"),
        )

    assert response.status_code == HTTPStatus.ACCEPTED
    assert response.json["access_token"] is not None


def test_login_user_unregistered_user(client_app: FlaskClient) -> None:
    """Tests the Login User Controller on an unregistered login attempt

    Args:
        client_app (FlaskClient): Test Client
    """
    with client_app as test_client:
        response = test_client.post(
            "/auth/login",
            json=dict(username="test", email="email@email.email", password="pswd"),
        )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert (
        response.json["message"]
        == "No user registered with those credentials. Please register to begin"
    )


def test_login_user_incorrect_credentials(
    register_test_user, client_app: FlaskClient
) -> None:
    """Tests Login User Controller when incorrect credentials are passed

    Args:
        register_test_user (any): Dummy test user record
        client_app (FlaskClient): Test Client
    """
    with client_app as test_client:
        response = test_client.post(
            "/auth/login",
            json=dict(username="tester", email="tester@email.com", password="passwd"),
        )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json["message"] == "Incorrect Credentials"


def test_logout(login_test_user, client_app: FlaskClient) -> None:
    """Tests the Logout User Controller

    Args:
        login_test_user (any): Dummy user's access token
        client_app (FlaskClient): Test Client
    """
    with client_app as test_client:
        response = test_client.delete(
            "/auth/logout",
            headers={
                "Authorization": f"Bearer {login_test_user}",
                "Content-Type": "application/json",
            },
        )

    assert response.status_code == HTTPStatus.OK
    assert response.json["message"] == "Access token revoked"


def test_logout_no_jwt_headers(client_app: FlaskClient) -> None:
    """Tests Logout User Controller when no bearer token header is supplied

    Args:
        client_app (FlaskClient): Test Client
    """
    with client_app as test_client:
        response = test_client.delete("/auth/logout")

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_register_new_user(client_app: FlaskClient) -> None:
    """Tests Register User Controller

    Args:
        client_app (FlaskClient): Test Client
    """
    with client_app as test_client:
        response = test_client.post(
            "/auth/register",
            json=dict(
                username="new_tester", email="new_tester@email.com", password="password"
            ),
        )
        response2 = test_client.post(
            "/auth/register",
            json=dict(
                username="another_new_tester",
                email="another_new_tester@email.com",
                password="password",
                is_admin=True,
            ),
        )

    assert response.status_code == HTTPStatus.CREATED
    assert response2.status_code == HTTPStatus.CREATED
    assert response.content_type == "application/json"
    assert response2.content_type == "application/json"


def test_register_conflicting_user(register_test_user, client_app: FlaskClient) -> None:
    """Tests Register User Controller with conflicting credentials

    Args:
        register_test_user (any): dummy registered test user
        client_app (FlaskClient): Test Client
    """
    with client_app as test_client:
        response = test_client.post(
            "/auth/register",
            json=dict(username="tester", email="tester@email.com", password="password"),
        )

        response2 = test_client.post(
            "/auth/register",
            json=dict(
                username="another_tester", email="tester@email.com", password="password"
            ),
        )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response2.status_code == HTTPStatus.CONFLICT
    assert response.json["message"] == "User already exists"
    assert (
        response2.json["message"] == "A user with the same credentials is registered."
    )
