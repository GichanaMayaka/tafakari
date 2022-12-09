from flask_sqlalchemy import SQLAlchemy

from ..configs import configs

SQLALCHEMY_DATABASE_URI: str = f"postgresql://%s:%s@%s:%s/%s" % (
    configs.APP_CONFIG.POSTGRES_USERNAME,
    configs.APP_CONFIG.POSTGRES_PASSWORD,
    configs.APP_CONFIG.POSTGRES_HOSTNAME,
    configs.APP_CONFIG.POSTGRES_PORT,
    configs.APP_CONFIG.POSTGRES_DATABASE_NAME
)

TEST_DATABASE_URI: str = "postgresql://postgres:password@localhost:5433/tafakariTest"

db = SQLAlchemy()


class CRUDMixin(object):
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)

    @classmethod
    def get_by_id(cls, id: int):
        if any((isinstance(id, str) and id.isdigit(),
                isinstance(id, (int, float))), ):
            return cls.query.get(int(id))
        return None

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        return instance.save()

    def save(self, commit: bool = True):
        db.session.add(self)

        if commit:
            db.session.commit()
        return self

    def update(self, commit=True, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        return commit and self.save() or self
