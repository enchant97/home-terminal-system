from datetime import datetime

from ..database import db


class Table_Updates(db.Model):
    """
    Stores tables and when they were last updated
    """
    __tablename__ = "table_updates"
    table_name = db.Column(db.String(length=128), primary_key=True)
    last_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
