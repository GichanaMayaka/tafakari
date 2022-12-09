from flask import Flask

from .commands import (create_tables, drop_db, recreate_db, seed, seed_posts,
                       seed_users, create_db)
from .database import SQLALCHEMY_DATABASE_URI, db
from .extensions import bcrypt, migrations
from .models.comments import Comments
from .models.posts import Post
from .models.subreddit import Subreddit
from .models.users import User
from .views.posts_views import posts
from .views.subreddits_views import subreddits
from .views.users_views import user
from ..configs import configs


def create_app(database_uri: str = SQLALCHEMY_DATABASE_URI, configurations: object = configs) -> Flask:
    app = Flask(__name__)
    app.config.from_object(configurations)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri

    register_extensions(app=app)
    register_commands(app=app)
    register_blueprints(app=app)

    @app.route("/", methods=["GET"])
    def index():
        return {
            "message": "Welcome to tafakari",
        }

    return app


def register_extensions(app: Flask) -> None:
    db.init_app(app=app)
    bcrypt.init_app(app=app)
    migrations.init_app(app=app)


def register_commands(app: Flask) -> None:
    for command in [create_db, create_tables, seed_users, drop_db, recreate_db, seed_posts, seed]:
        app.cli.command()(command)


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(blueprint=user)
    app.register_blueprint(blueprint=subreddits)
    app.register_blueprint(blueprint=posts)


if __name__ == "__main__":
    create_app()
