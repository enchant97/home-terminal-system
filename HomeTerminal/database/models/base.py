"""
contains base models that are not
created as they are abstract,
allows access to the db obj from database.py
"""
from datetime import datetime

from ..database import db


class BaseNoUpdate(db.Model):
    """
    Base row without last_updated

    contains:
        id
        removed
    """
    __abstract__ = True
    id_ = db.Column("id", db.Integer, primary_key=True)
    removed = db.Column(db.Boolean, nullable=False, default=False)

# Source: https://stackoverflow.com/a/37515941
class Base(BaseNoUpdate):
    """
    The Base row model

    contains:
        id
        last_updated
        removed
    """
    __abstract__ = True
    last_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def update_last_updated(self):
        """
        Update the last_updated column
        with the current datetime.utcnow()
        """
        self.last_updated = datetime.utcnow()
