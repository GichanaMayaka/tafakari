from http import HTTPStatus

import pytest
from flask import Flask
from flask.testing import FlaskClient
from flask_login import FlaskLoginClient
from sqlalchemy import create_engine
from sqlalchemy_utils import create_database, database_exists, drop_database

from . import test_database_uri
from ..tafakari import create_app
from ..tafakari.database import db
from ..tafakari.models import *
from ..tafakari.views.schemas import CreateSubredditPostSchema

engine = create_engine(
    test_database_uri,
    pool_pre_ping=True,
    connect_args={
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
    }
)


@pytest.fixture()
def create_test_database(db_engine=engine) -> None:
    if not database_exists(db_engine.url):
        create_database(db_engine.url)


@pytest.fixture()
def app(create_test_database) -> Flask:
    yield create_app(database_uri=test_database_uri)


@pytest.fixture()
def test_client_app(app) -> FlaskClient:
    with app.app_context():
        db.metadata.create_all(bind=engine)
        yield app
        drop_database(engine.url)


@pytest.fixture(autouse=True)
def login_client(test_client_app):
    test_client_app.test_client_class = FlaskLoginClient
    yield test_client_app


def test_create_subreddit_valid(login_client) -> None:
    u = users.User.create(
        username="tester",
        email="tester@email.com",
        password="password"
    )
    with login_client.test_client(user=u) as test_client:
        response = test_client.post(
            "/create/subreddit",
            json=CreateSubredditPostSchema(
                name="test",
                description="test"
            ).dict()
        )
    assert response.content_type == "application/json"
    assert response.status_code == HTTPStatus.OK


def test_create_subreddit_unauthorised(login_client) -> None:
    with login_client.test_client() as test_client:
        response = test_client.post(
            "/create/subreddit",
            json=CreateSubredditPostSchema(
                name="test",
                description="test"
            ).dict()
        )

    assert response.content_type == "application/json"
    assert response.status_code == HTTPStatus.UNAUTHORIZED
