from http import HTTPStatus

import pytest
from flask import Flask
from flask.testing import FlaskClient
from flask_jwt_extended import create_access_token
from sqlalchemy import create_engine
from sqlalchemy_utils import create_database, database_exists, drop_database

from . import test_database_uri
from ..tafakari import create_app
from ..tafakari.controllers.schemas import CreateSubredditPostSchema
from ..tafakari.database import db
from ..tafakari.models.subreddit import Subreddit
from ..tafakari.models.users import User

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
def client_app(app) -> FlaskClient:
    with app.app_context():
        db.metadata.create_all(bind=engine)
        yield app
        db.session.remove()
        drop_database(engine.url)


@pytest.fixture(autouse=True)
def client(client_app) -> FlaskClient:
    yield client_app.test_client()


def test_create_subreddit_valid(client: FlaskClient) -> None:
    subreddit_name = "test_subreddit"
    subreddit_description = "test_subreddit_description"

    with client as test_client:
        fake_user = User.create(username="test_user", email="tester@email.com", password="password")
        fake_user.save()
        fake_user_token = create_access_token(identity=fake_user.username, fresh=True)

        response = test_client.post(
            "/create/subreddit",
            headers={"Authorization": f"Bearer {fake_user_token}"},
            json=CreateSubredditPostSchema(
                name=subreddit_name,
                description=subreddit_description
            ).dict()
        )

    assert response.status_code == HTTPStatus.OK
    assert response.json == {"message": "created"}

    # And the new subreddit should be in the database
    test_subreddit = Subreddit.query.filter_by(name=subreddit_name).first()
    assert test_subreddit is not None
    assert test_subreddit.description == subreddit_description
    assert test_subreddit.users[0].username == fake_user.username


def test_create_subreddit_unauthorised(client: FlaskClient) -> None:
    with client as test_client:
        response = test_client.post(
            "/create/subreddit",
            json=CreateSubredditPostSchema(
                name="test",
                description="test"
            ).dict()
        )

    assert response.content_type == "application/json"
    assert response.status_code == HTTPStatus.UNAUTHORIZED
