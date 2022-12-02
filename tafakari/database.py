from flask_sqlalchemy import SQLAlchemy

SQLALCHEMY_DATABASE_URI: str = "postgresql://postgres:password@localhost:5432/tafakari"

db = SQLAlchemy()
