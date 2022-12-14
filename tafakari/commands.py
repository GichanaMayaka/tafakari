import click
from faker import Faker
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.engine.mock import MockConnection
from sqlalchemy_utils import create_database, database_exists, drop_database

from .database import db, SQLALCHEMY_DATABASE_URI
from .models.users import User


def database_engine(uri: str) -> MockConnection:
    engine = create_engine(
        uri
    )
    return engine


def create_db(uri: str = SQLALCHEMY_DATABASE_URI) -> None:
    engine = database_engine(uri)

    if not database_exists(engine.url):
        create_database(engine.url)


def create_tables(database: SQLAlchemy = db) -> None:
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
            password="password",
            is_admin=True
        )
    )

    for user in users:
        db.session.add(user)

    db.session.commit()


def drop_tables() -> None:
    """Drops the database."""
    if click.confirm('Are you sure?', default=False, abort=True):
        db.drop_all()


def recreate_db() -> None:
    """Same as running drop_db() and create_db()."""
    drop_tables()
    create_tables()


def drop_db() -> None:
    engine = database_engine(uri=SQLALCHEMY_DATABASE_URI)
    if database_exists(engine.url):
        drop_database(engine.url)
