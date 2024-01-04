import pendulum

from ..database import db


class CRUDMixin(object):
    """CRUD Mixins Class

    Args:
        object (object): Base class
    """

    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, unique=True, primary_key=True, autoincrement=True)
    modified_on = db.Column(
        db.DateTime(timezone=True), default=pendulum.now, nullable=False
    )

    @classmethod
    def get_by_id(cls, id: int):
        if any(
            (isinstance(id, str) and id.isdigit(), isinstance(id, (int, float))),
        ):
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

    def delete(self, commit: bool = True, **kwargs):
        db.session.delete(self)

        if commit:
            db.session.commit()
        return self

    def update(self, commit: bool = True, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        return commit and self.save() or self
