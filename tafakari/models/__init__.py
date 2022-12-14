from ..database import db

__all__: object = [
    "comments",
    "posts",
    "subreddit",
    "users"
]


class CRUDMixin(object):
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

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

    def delete(self, commit: bool = True, **kwargs):
        db.session.delete(self)

        if commit:
            db.session.commit()
        return self

    def update(self, commit: bool = True, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        return commit and self.save() or self
