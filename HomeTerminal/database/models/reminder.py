"""
contains the reminder models
"""
from datetime import datetime

from .base import Base, db
from .user import User


class Reminder_Type(Base):
    """
    The reminder_type table for storing reminder types
    """
    __tablename__ = "reminder_types"
    type_name = db.Column(db.String(length=1500), nullable=False)


class Reminder(Base):
    """
    The reminder table for storing main content of reminders
    """
    __tablename__ = "reminders"
    content = db.Column(db.String(length=1500), nullable=False)
    user_id_for = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    reminder_type_id = db.Column(db.Integer, db.ForeignKey("reminder_types.id"), nullable=False)
    is_priority = db.Column(db.Boolean, nullable=False, default=False)
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    reminder_type = db.relation(Reminder_Type, backref=__tablename__)
    user = db.relation(User, backref=__tablename__)
