import datetime
import os
from typing import Final

from pydantic import BaseSettings, PostgresDsn


class BaseConfigs(BaseSettings):
    """Base Configurations for tafakari parsed from a .env.* file

    Args:
        BaseSettings (Any): Base Class
    """

    POSTGRES_DSN: PostgresDsn

    SESSION_TYPE: str

    SECRET_KEY: str
    JWT_ALGORITHM: Final[str] = "HS256"
    JWT_ACCESS_TOKEN_EXPIRES: datetime.timedelta = datetime.timedelta(minutes=30)

    REDIS_HOSTNAME: str
    REDIS_PORT: int
    DEBUG: bool = True

    CACHE_TYPE: str = "RedisCache"
    CACHE_DEFAULT_TIMEOUT: int

    TESTING: bool = False

    class Config:
        """Environment Configuration"""

        env_file = ".env"
        env_file_encoding = "utf-8"


class DevConfig(BaseConfigs):
    """Development configurations."""

    DEBUG: Final[bool] = True


class ProdConfig(BaseConfigs):
    """Production configurations."""

    DEBUG: Final[bool] = False

    class Config:
        """Environment Configurations"""

        env_file = ".env.prod"


class TestConfig(DevConfig):
    """Testing configurations"""

    TESTING: Final[bool] = True

    class Config:
        """Environment Configurations"""

        env_file = ".env.test"


def factory() -> DevConfig | TestConfig | ProdConfig:
    """Configuration Factory function

    Returns:
        DevConfig | TestConfig | ProdConfig: Configurations
    """
    env = os.environ.get("ENV", "dev")
    environment = {"dev": DevConfig, "prod": ProdConfig, "test": TestConfig}.get(
        env.lower()
    )

    if not environment:
        raise ValueError(
            f"Invalid environment: {env}. Please use either: dev, test, or prod"
        )

    config = environment()

    return config


configs = factory()
