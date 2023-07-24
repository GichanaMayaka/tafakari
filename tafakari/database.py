from typing import Final

from flask_sqlalchemy import SQLAlchemy

from ..configs import configs

SQLALCHEMY_DATABASE_URI: Final[str] = configs.POSTGRES_DSN

db = SQLAlchemy()
