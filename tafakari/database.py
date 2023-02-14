from typing import Final

from flask_sqlalchemy import SQLAlchemy

from ..configs import configs

SQLALCHEMY_DATABASE_URI: Final[str] = "postgresql://%s:%s@%s:%s/%s" % (
    configs.APP_CONFIG.POSTGRES_USERNAME,
    configs.APP_CONFIG.POSTGRES_PASSWORD,
    configs.APP_CONFIG.POSTGRES_HOSTNAME,
    configs.APP_CONFIG.POSTGRES_PORT,
    configs.APP_CONFIG.POSTGRES_DATABASE_NAME
)

db = SQLAlchemy()
