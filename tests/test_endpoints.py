import os

import pytest
from flask import Flask
from flask.testing import FlaskClient

from ..configs import configs
from ..tafakari import create_app
from ..tafakari.views.schemas import CreateSubredditPostSchema


@pytest.fixture()
def app() -> Flask:
    return create_app(configurations=configs)


@pytest.fixture()
def test_client(app) -> FlaskClient:
    return app.test_client()


def test_create_subreddit(test_client) -> None:
    response = test_client.post(
        "/create/subreddit",
        json=CreateSubredditPostSchema(
            name="test",
            description="test"
        ).dict()
    )
    assert response.content_type == "application/json"
    assert response.status_code == 200
