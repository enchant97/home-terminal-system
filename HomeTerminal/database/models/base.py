"""
contains base models that are not
created as they are abstract,
allows access to the db obj from database.py
"""
from datetime import datetime

from ..database import db


# Source: https://stackoverflow.com/a/37515941
class Base(db.Model):
    """
    The Base row model

    contains:
        id
        last_updated
        removed
    """
    __abstract__ = True
    id_ = db.Column("id", db.Integer, primary_key=True)
    last_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    removed = db.Column(db.Boolean, nullable=False, default=False)

    def update_last_updated(self):
        """
        Update the last_updated column
        with the current datetime.utcnow()
        """
        self.last_updated = datetime.utcnow()
