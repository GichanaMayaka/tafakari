from flask import Flask

from .commands import (create_db, create_tables, drop_db, drop_tables,
                       recreate_db, seed, seed_users)
from .controllers.authentication import authentications
from .controllers.comments import comments
from .controllers.posts import posts
from .controllers.subreddits import subreddits
from .controllers.users import user
from .database import SQLALCHEMY_DATABASE_URI, db
from .extensions import bcrypt, jwt, sess
from ..configs import configs


def create_app(database_uri: str = SQLALCHEMY_DATABASE_URI, configurations: object = configs,
               additional_binds: dict = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(configurations)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri

    if additional_binds:
        app.config["SQLALCHEMY_BINDS"] = additional_binds

    register_extensions(app=app)
    register_commands(app=app)
    register_blueprints(app=app)

    @app.route("/", methods=["GET"])
    def index():
        return {
            "message": "Welcome to tafakari",
        }, 200

    @app.after_request
    def set_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allowed-Methods"] = "GET, POST"
        response.headers["Content-Type"] = "application/json"
        return response

    return app


def register_extensions(app: Flask) -> None:
    db.init_app(app=app)
    bcrypt.init_app(app=app)
    sess.init_app(app=app)
    jwt.init_app(app=app)


def register_commands(app: Flask) -> None:
    for command in [create_db, drop_db, recreate_db, create_tables, drop_tables, seed_users, seed]:
        app.cli.command()(command)


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(blueprint=user)
    app.register_blueprint(blueprint=subreddits)
    app.register_blueprint(blueprint=posts)
    app.register_blueprint(blueprint=authentications)
    app.register_blueprint(blueprint=comments)


if __name__ == "__main__":
    create_app()
