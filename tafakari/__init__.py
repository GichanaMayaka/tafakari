import os

from flask import Flask, Response, request

from tafakari.configs import configs

from .commands import (
    create_db,
    create_tables,
    drop_db,
    drop_tables,
    recreate_db,
    seed,
    seed_users,
)
from .controllers.authentication import authentications
from .controllers.comments import comments
from .controllers.posts import posts
from .controllers.subreddits import subreddits
from .controllers.users import user
from .database import SQLALCHEMY_DATABASE_URI, db
from .extensions import bcrypt, cache, cors, jwt, limiter, migrations
from .utils import configure_logger, get_client_ip_address


def create_app(
    database_uri: str = SQLALCHEMY_DATABASE_URI,
    configurations: object = configs,
    additional_binds: dict | None = None,
) -> Flask:
    """Application Factory

    Args:
        database_uri (str, optional): Database URI. Defaults to SQLALCHEMY_DATABASE_URI.
        configurations (object, optional): Configurations. Defaults to configs.
        additional_binds (dict, optional): Additional Binds. Defaults to None.

    Returns:
        Flask: Flask App Object
    """
    app = Flask(__name__)
    app.config.from_object(configurations)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri

    logger = configure_logger(log_path="./tafakari.log")
    app.logger.addHandler(logger)

    if additional_binds:
        app.config["SQLALCHEMY_BINDS"] = additional_binds

    env = os.getenv("ENV")
    if env == "test" or env == "dev":
        # Disable rate-limiting according to the environment
        limiter.enabled = False

    register_extensions(app=app)
    register_commands(app=app)
    register_blueprints(app=app)

    @app.route("/", methods=["GET"])
    @limiter.exempt
    def index():
        return "Welcome to tafakari", 200

    @app.route("/ping", methods=["GET"])
    @limiter.exempt
    def ping():
        return "PONG! \nWelcome to tafakari", 200

    @app.before_request
    def extract_ip_address() -> None:
        ip_address = get_client_ip_address(request)
        app.logger.info(
            "Request received from %s: Method: %s, for URL: %s",
            f"{ip_address}",
            request.method,
            request.url,
        )

    @app.after_request
    def set_headers(response: Response) -> Response:
        """Sets Headers on each response

        Args:
            response (Response): The Response Object

        Returns:
            Response: The Response with headers set
        """
        response.headers["Access-Control-Allowed-Methods"] = "GET, POST, DELETE, PUT"
        response.headers["Content-Type"] = "application/json"
        response.headers["Cache-Control"] = "no-cache"
        return response

    return app


def register_extensions(app: Flask) -> None:
    """Register application's extensions

    Args:
        app (Flask): The Flask App Object
    """
    db.init_app(app=app)
    bcrypt.init_app(app=app)
    jwt.init_app(app=app)
    cache.init_app(
        app=app,
        config={
            "CACHE_REDIS_HOST": configs.REDIS_HOSTNAME,
            "CACHE_REDIS_PORT": configs.REDIS_PORT,
            "CACHE_KEY_PREFIX": "tafakari_",
            "CACHE_REDIS_DB": 1,
            "DEBUG": configs.DEBUG,
            "CACHE_TYPE": configs.CACHE_TYPE,
            "CACHE_DEFAULT_TIMEOUT": configs.CACHE_DEFAULT_TIMEOUT,
        },
    )
    cors.init_app(app=app)
    migrations.init_app(app=app, db=db)
    limiter.init_app(app=app)


def register_commands(app: Flask) -> None:
    """Register application's terminal/CLI commands

    Args:
        app (Flask): The Flask App Object
    """
    for command in [
        create_db,
        drop_db,
        recreate_db,
        create_tables,
        drop_tables,
        seed_users,
        seed,
    ]:
        app.cli.command()(command)


def register_blueprints(app: Flask) -> None:
    """Register application's routes Blueprints

    Args:
        app (Flask): The Flask App Object
    """
    app.register_blueprint(blueprint=user)
    app.register_blueprint(blueprint=subreddits)
    app.register_blueprint(blueprint=posts)
    app.register_blueprint(blueprint=authentications)
    app.register_blueprint(blueprint=comments)
