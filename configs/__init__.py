import datetime
import os
from typing import Final

from pydantic import BaseSettings, PostgresDsn


class DevConfig(BaseSettings):
    """Development configurations."""
    POSTGRES_DSN: PostgresDsn

    SESSION_TYPE: str

    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRES: Final[datetime.timedelta] = datetime.timedelta(minutes=30)

    REDIS_HOSTNAME: str
    REDIS_PORT: int
    DEBUG: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_prefix: str = "DEV_"


class ProdConfig(DevConfig):
    """Production configurations."""

    class Config:
        env_prefix: str = "PROD_"


class TestConfig(DevConfig):
    TESTING: Final[bool] = True


def factory():
    env: str = os.environ.get("ENV", "dev")

    development = DevConfig()
    testing = TestConfig()
    production = ProdConfig()

    env = env.lower()

    if env == "dev":
        return development
    elif env == "test":
        return testing
    elif env == "prod":
        return production


configs = factory()
