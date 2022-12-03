from flask import Flask

from .database import db, SQLALCHEMY_DATABASE_URI
from .models.users import User
from .models.subreddit import Subreddit
from .models.posts import Post
from .models.comments import Comments
from .commands import create_db, seed_users, drop_db, recreate_db
from .extensions import bcrypt


def create_app(configs: object = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(configs)
    app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI

    register_extensions(app=app)
    register_commands(app=app)

    @app.route("/", methods=["GET"])
    def index():
        return {
            "message": "Welcome to tafakari"
        }

    return app


def register_extensions(app: Flask) -> None:
    db.init_app(app=app)
    bcrypt.init_app(app=app)


def register_commands(app: Flask) -> None:
    for command in [create_db, seed_users, drop_db, recreate_db]:
        app.cli.command()(command)
