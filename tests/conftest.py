from http import HTTPStatus

import pytest
from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy import create_engine
from sqlalchemy_utils import create_database, database_exists, drop_database

from tafakari import create_app
from tafakari.configs import configs
from tafakari.tafakari import db

engine = create_engine(configs.POSTGRES_DSN)


@pytest.fixture()
def create_test_database(db_engine=engine) -> None:
    if not database_exists(db_engine.url):
        create_database(db_engine.url)


@pytest.fixture()
def app(create_test_database) -> Flask:
    yield create_app()


@pytest.fixture()
def client_app(app: Flask) -> FlaskClient:
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        drop_database(engine.url)


@pytest.fixture()
def register_test_user(client_app: FlaskClient) -> None:
    """Registers a test user

    Args:
        client_app (FlaskClient): The Flask Test Client
    """
    with client_app as test_client:
        test_client.post(
            "/auth/register",
            json=dict(username="tester", email="tester@email.com", password="password"),
        )


@pytest.fixture(autouse=True)
def login_test_user(client_app: FlaskClient, register_test_user) -> str:
    with client_app as test_client:
        response = test_client.post(
            "/auth/login",
            json=dict(username="tester", email="tester@email.com", password="password"),
        )

    assert response.status_code == HTTPStatus.ACCEPTED

    return response.json["access_token"]


@pytest.fixture(autouse=True)
def create_mock_subreddit(client_app, login_test_user) -> dict:
    mock_subreddit = dict(name="Test Subreddit", description="This is a test Subreddit")

    with client_app as test_client:
        response = test_client.post(
            "/subreddits",
            json=mock_subreddit,
            headers={
                "Authorization": f"Bearer {login_test_user}",
                "Content-Type": "application/json",
            },
        )

        assert response.status_code == HTTPStatus.CREATED

        return response.json


@pytest.fixture(autouse=True)
def create_mock_post(client_app, login_test_user, create_mock_subreddit) -> dict:
    mock_post = dict(title="Test Post", text="Test Post", subreddit_id=1)

    with client_app as test_client:
        response = test_client.post(
            "/posts",
            json=mock_post,
            headers={
                "Authorization": f"Bearer {login_test_user}",
                "Content-Type": "application/json",
            },
        )

        assert response.status_code == HTTPStatus.CREATED

        return response.json
