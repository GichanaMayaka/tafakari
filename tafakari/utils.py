from logging import Logger, getLogger
from logging.config import dictConfig

from flask import Flask, Request


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
