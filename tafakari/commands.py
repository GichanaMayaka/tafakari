import click
from faker import Faker
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy

from .database import db
from .models.users import User


@with_appcontext
def create_db(database: SQLAlchemy = db) -> None:
    database.create_all()


@click.option("--num_users", default=3, help="number of users")
def seed_users(num_users: int) -> None:
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


def drop_db() -> None:
    """Drops the database."""
    if click.confirm('Are you sure?', abort=True):
        db.drop_all()


def recreate_db() -> None:
    """Same as running drop_db() and create_db()."""
    drop_db()
    create_db()
