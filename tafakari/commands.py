import random

import click
from faker import Faker
from flask_sqlalchemy import SQLAlchemy

from .database import db
from .models.posts import Post
from .models.users import User


def create_db(database: SQLAlchemy = db) -> None:
    database.create_all()


@click.option("--num_users", default=3, help="number of users")
def seed(num_users: int) -> list:
    fakes = Faker()
    users = []

    for _ in range(num_users):
        users.append(
            User(
                username=fakes.user_name(),
                email=fakes.email(),
                password="password"
            )
        )

    for user in users:
        db.session.add(user)

    db.session.commit()

    return users


@click.option("--num_users", default=3, help="number of users")
def seed_users(num_users: int) -> None:
    users: list = seed(num_users)

    users.append(
        User(
            username="gichana",
            email="gichana@email.com",
            password="password"
        )
    )

    for user in users:
        db.session.add(user)

    db.session.commit()


@click.option("--num_posts", default=18, help="number of posts")
def seed_posts(num_posts: int) -> None:
    fakes = Faker()
    posts = []

    for _ in range(num_posts):
        posts.append(
            Post(
                title=fakes.sentence(),
                text=fakes.text(),
                created_by=random.randint(1, 3)
            )
        )

    for post in posts:
        db.session.add(post)

    db.session.commit()


def drop_db() -> None:
    """Drops the database."""
    if click.confirm('Are you sure?', abort=True):
        db.drop_all()


def recreate_db() -> None:
    """Same as running drop_db() and create_db()."""
    drop_db()
    create_db()
