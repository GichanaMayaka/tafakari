import datetime
import secrets
from typing import Final, Any

from pydantic import BaseSettings, BaseModel, Field


class AppConfig(BaseModel):
    POSTGRES_HOSTNAME: Final[str] = "localhost"
    POSTGRES_USERNAME: Final[str] = "postgres"
    POSTGRES_PASSWORD: Final[str] = "password"
    POSTGRES_DATABASE_NAME: Final[str] = "tafakari"
    POSTGRES_PORT: Final[int] = 5433
    
    SESSION_TYPE: Final[str] = "redis"
    
    SECRET_KEY: Final[str] = secrets.token_hex()
    JWT_ALGORITHM: Final[str] = "HS256"
    JWT_ACCESS_TOKEN_EXPIRES: Final[datetime.timedelta] = datetime.timedelta(minutes=30)
    
    REDIS_HOSTNAME: Final[str] = "localhost"
    REDIS_PORT: Final[int] = 6379


class GlobalConfig(BaseSettings):
    APP_CONFIG: AppConfig = AppConfig()
    ENV_STATE: str = Field(None, env="ENV_STATE")

    class Config:
        env_file: str = ".env"


class DevConfig(GlobalConfig):
    """Development configurations."""
    DEBUG: Final[bool] = True

    class Config:
        env_prefix: str = "DEV_"


class ProdConfig(GlobalConfig):
    """Production configurations."""

    class Config:
        env_prefix: str = "PROD_"


class TestConfig(GlobalConfig):
    TESTING: Final[bool] = True


class FactoryConfig:
    """Returns a config instance depending on the ENV_STATE variable."""

    def __init__(self, env_state: str):
        self.env_state = env_state.lower()

    def __call__(self):
        if self.env_state == "dev":
            return DevConfig()

        if self.env_state == "prod":
            return ProdConfig()

        if self.env_state == "test":
            return TestConfig()


configs = FactoryConfig(GlobalConfig().ENV_STATE)()
