"""
contains the reminder models
"""
from datetime import datetime

from .base import Base, db

class Reminder_Type(Base):
    """
    The reminder_type table for storing reminder types
    """
    __tablename__ = "reminder_type"
    type_name = db.Column(db.String(length=1500), nullable=False)

class Reminder(Base):
    """
    The reminder table for storing main content of reminders
    """
    __tablename__ = "reminder"
    content = db.Column(db.String(length=1500), nullable=False)
    user_for = db.Column(db.String(length=80), db.ForeignKey("user.username"), nullable=True)
    reminder_type = db.Column(db.Integer, db.ForeignKey("reminder_type.id"), nullable=False)
    is_priority = db.Column(db.Boolean, nullable=False, default=False)
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
