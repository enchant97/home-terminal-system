"""
contains the homework manager models
"""
from datetime import datetime

from .base import Base, db


class Main(Base):
    """
    The homework main entry
    """
    __tablename__ = "hw_mains"
    message = db.Column(db.String(length=1500), nullable=False)
    datedue = db.Column(db.DateTime, nullable=False)

    def get_day_first_date(self):
        """
        returns datedue as format '%d-%m-%Y'
        """
        return datetime.strftime(self.datedue, "%d-%m-%Y")

    def serialize(self):
        """
        get data as dict,
        uses get_day_first_date() for datedue
        """
        return {
            "id":self.id_,
            "message":self.message,
            "datedue":datetime.strftime(self.datedue, "%Y-%m-%d")
        }

class Task(Base):
    """
    The homework task, allowing for
    multiple tasks on one homework
    """
    __tablename__ = "hw_tasks"
    hw_id = db.Column(db.Integer, db.ForeignKey("hw_mains.id"), nullable=False)
    content = db.Column(db.String(length=2000), nullable=False)

    hw_main = db.relation(Main, backref=__tablename__)

    def serialize(self):
        return {
            "id":self.id_,
            "hw_id":self.hw_id,
            "content":self.content
        }
