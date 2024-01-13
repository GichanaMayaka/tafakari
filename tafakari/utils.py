from logging import Logger, getLogger
from logging.config import dictConfig
from typing import Any, Callable, Final

from flask import Flask, Request

from .extensions import cache
from ..configs import configs


def get_client_ip_address(client_request: Request) -> str | None:
    """Extracts client's IP address from Headers

    Args:
        request (request): The client's request

    Returns:
        str | None: The IP Address
    """
    forwarded_for = client_request.headers.getlist("X-Forwarded-For")

    if forwarded_for:
        ip_address = forwarded_for[0]  # Usually the first IP is the client's
    else:
        ip_address = client_request.remote_addr

    return ip_address


def configure_logger(log_path: str, name: str = "default") -> Logger:
    """Configures the Application's Logger

    Args:
        log_path (str): The system file path to write logs to
        name (str, optional): Name of the Logger. Defaults to "default".

    Returns:
        Logger: The Application's Logger
    """
    dictConfig(
        {
            "version": 1,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                }
            },
            "handlers": {
                "console": {
                    "level": "INFO",
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "stream": "ext://sys.stdout",
                },
                "file": {
                    "level": "INFO",
                    "class": "logging.handlers.TimedRotatingFileHandler",
                    "formatter": "default",
                    "when": "midnight",
                    "filename": log_path,
                    "backupCount": 5,
                },
            },
            "loggers": {"default": {"level": "INFO", "handlers": ["console", "file"]}},
            "disable_existing_loggers": False,
        }
    )
    return getLogger(name)


def get_logger_instance(current_app: Flask) -> Logger:
    """Returns the configured logger from the running Flask App

    Args:
        current_app (Flask): The current running Flask App

    Yields:
        Logger: The Logger Object
    """
    with current_app.app_context():
        logger = current_app.logger

    return logger


CACHE_KEYS_REFERENCE: Final[dict[str, str | Callable]] = {
    "PROFILE": lambda username: f"{username}_profile",
    "ALL_SUBREDDITS": "all_subs",
    "SUBREDDIT_ID": lambda subreddit_id: f"subreddit_{subreddit_id}",
    "ALL_POSTS": "all_posts",
    "POST_ID": lambda post_id: f"post_{post_id}",
    "ALL_POSTS_IN_SUBREDDIT": lambda subreddit_id: f"all_posts_in_subreddit_{subreddit_id}",
}


def cache_invalidator(cache_key: str | list | None = None) -> bool:
    """Invalidates a key from Cache

    Args:
        cache_key (str, list, optional): The Key or list of keys to Invalidate. Defaults to None.

    Returns:
        bool: Returns True if successful, otherwise False
    """
    if isinstance(cache_key, list):
        return cache.delete_many(*cache_key)

    return cache.delete(cache_key)


def cache_setter(
    cache_key: str, value: Any, timeout: int = configs.CACHE_DEFAULT_TIMEOUT
) -> bool | None:
    """Sets a key in Cache

    Args:
        cache_key (str): The Cache Key
        value (Any): The Value to set in Cache
        timeout (int, optional): The TTL in Seconds. Defaults to configs.CACHE_DEFAULT_TIMEOUT.

    Returns:
        bool | None: Returns True if successful, otherwise False
    """
    return cache.set(cache_key, value, timeout=timeout)
