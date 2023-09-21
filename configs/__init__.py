import datetime
import os
from typing import Final

from pydantic import BaseSettings, PostgresDsn


class DevConfig(BaseSettings):
    """Development configurations."""
    POSTGRES_DSN: PostgresDsn

    SESSION_TYPE: str

    SECRET_KEY: str
    JWT_ALGORITHM: Final[str] = "HS256"
    JWT_ACCESS_TOKEN_EXPIRES: Final[datetime.timedelta] = datetime.timedelta(minutes=30)

    REDIS_HOSTNAME: str
    REDIS_PORT: int
    DEBUG: Final[bool] = True

    CACHE_TYPE: Final[str] = "RedisCache"
    CACHE_DEFAULT_TIMEOUT: int

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_prefix: Final[str] = "DEV_"


class ProdConfig(DevConfig):
    """Production configurations."""
    DEBUG: Final[bool] = False

    class Config:
        env_prefix: Final[str] = "PROD_"


class TestConfig(DevConfig):
    TESTING: Final[bool] = True

    class Config:
        env_prefix: Final[str] = "TEST_"


def factory():
    env = os.environ.get("ENV", "dev")

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
