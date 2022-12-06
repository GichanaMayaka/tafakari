from typing import Optional, Final

from pydantic import BaseSettings, BaseModel, Field


class AppConfig(BaseModel):
    POSTGRES_HOSTNAME: Final[str] = "localhost"
    POSTGRES_USERNAME: Final[str] = "postgres"
    POSTGRES_PASSWORD: Final[str] = "password"
    POSTGRES_DATABASE_NAME: Final[str] = "tafakari"
    POSTGRES_PORT: Final[int] = 5432


class GlobalConfig(BaseSettings):
    APP_CONFIG: AppConfig = AppConfig()
    ENV_STATE: Optional[str] = Field(None, env="ENV_STATE")

    class Config:
        env_file: str = ".env"


class DevConfig(GlobalConfig):
    """Development configurations."""

    class Config:
        env_prefix: str = "DEV_"


class ProdConfig(GlobalConfig):
    """Production configurations."""

    class Config:
        env_prefix: str = "PROD_"


class TestConfig(GlobalConfig):
    TESTING: Final[bool] = True
    POSTGRES_DATABASE_NAME: Final[str] = "testTafakari"


class FactoryConfig:
    """Returns a config instance dependending on the ENV_STATE variable."""

    def __init__(self, env_state: Optional[str]):
        self.env_state = env_state

    def __call__(self):
        if self.env_state == "dev":
            return DevConfig()

        elif self.env_state == "prod":
            return ProdConfig()

        elif self.env_state == "test":
            return TestConfig()


configs = FactoryConfig(GlobalConfig().ENV_STATE)()
