from datetime import datetime

from ..database import db


class Homework_Main(db.Model):
    """
    The homework main entry
    """
    __tablename__ = "homework_main"
    id_ = db.Column("id", db.Integer, primary_key=True)
    message = db.Column("message", db.String(length=1500), nullable=False)
    datedue = db.Column("datedue", db.DateTime, nullable=False)
    removed = db.Column("removed", db.Integer, nullable=False, default=0)

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

class Homework_Task(db.Model):
    """
    The homework task, allowing for
    multiple tasks on one homework
    """
    __tablename__ = "homework_task"
    id_ = db.Column("id", db.Integer, primary_key=True)
    hw_id = db.Column("hw_id", db.Integer, db.ForeignKey("homework_main.id"), nullable=False)
    content = db.Column("content", db.String(length=2000), nullable=False)
    removed = db.Column("removed", db.Integer, nullable=False, default=0)

    def serialize(self):
        return {
            "id":self.id_,
            "hw_id":self.hw_id,
            "content":self.content
        }
