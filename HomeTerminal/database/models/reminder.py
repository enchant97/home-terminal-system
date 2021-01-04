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
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.String(length=1500), nullable=False)
    user_id_for = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    reminder_type_id = db.Column(
        db.Integer, db.ForeignKey("reminder_types.id"),
        nullable=False)
    is_priority = db.Column(db.Boolean, nullable=False, default=False)
    datedue = db.Column(db.DateTime)

    reminder_type = db.relation(Reminder_Type, backref=__tablename__)
    user_for = db.relation(User, backref=__tablename__)

    def get_day_first_date(self):
        """
        returns datedue as format '%d-%m-%Y'
        """
        #TODO remove in future (make a helper func to get 'human' datetime)
        if self.datedue:
            return datetime.strftime(self.datedue, "%d-%m-%Y")


    def serialize(self):
        """
        get data as dict,
        uses ISO 8601 for datetime
        """
        return {
            "created_at": datetime.strftime(self.created_at, "%Y-%m-%d"),
            "id":self.id_,
            "content": self.content,
            "user_id_for": self.user_id_for,
            "type_id": self.reminder_type_id,
            "is_priority": self.is_priority,
            "datedue": datetime.strftime(self.datedue, "%Y-%m-%d")
        }

class Reminder_Task(Base):
    """
    reminder task table for sub tasks in a reminder
    """
    __tablename__ = "reminder_tasks"
    reminder_id = db.Column(db.Integer, db.ForeignKey("reminders.id"), nullable=False)
    name = db.Column(db.String(length=1500), nullable=False)

    def serialize(self):
        """
        get data as dict
        """
        return {
            "id": self.id_,
            "reminder_id": self.reminder_id,
            "name": self.name
        }
