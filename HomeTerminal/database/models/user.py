from datetime import datetime

from flask_login import UserMixin

from ..database import db


class User(UserMixin, db.Model):
    """
    Stores info about users
    """
    __tablename__ = "user"
    username = db.Column("username", db.String(length=80), primary_key=True)
    password = db.Column("password", db.String(length=128), nullable=False)
    lastlogin = db.Column("lastlogin", db.DateTime, nullable=False, default=datetime.now)
    birthday = db.Column("birthday", db.DateTime, nullable=False)
    removed = db.Column("removed", db.Integer, nullable=False, default=0)

    def get_id(self):
        return self.username

    def __repr__(self):
        return f"username={self.username}, lastlogin={self.lastlogin}"

class User_Settings(db.Model):
    """
    Where user settings are stored.
    Each user should have one of these
    """
    __tablename__ = "user_settings"
    username = db.Column(
        "username", db.String(length=80),
        db.ForeignKey("user.username"), primary_key=True)
    fm_notif = db.Column("fm_notif", db.Integer, nullable=False, default=0)
    hwm_notif = db.Column("hwm_notif", db.Integer, nullable=False, default=0)
    mess_notif = db.Column("mess_notif", db.Integer, nullable=False, default=0)

    def serialize(self):
        return {
            "fm_notif":self.fm_notif,
            "hwm_notif":self.hwm_notif,
            "mess_notif":self.mess_notif
        }

class Api_Key(db.Model):
    """
    Stores api keys and registers each owner
    """
    __tablename__ = "api_key"
    key = db.Column("key", db.String(length=128), primary_key=True)
    owner = db.Column(
        "owner", db.String(length=80),
        db.ForeignKey("user.username"), nullable=False)
    removed = db.Column("removed", db.Integer, nullable=False, default=0)

class Message(db.Model):
    __tablename__ = "message"
    id_ = db.Column("id", db.Integer, primary_key=True)
    user_from = db.Column(
        "user_from", db.String(length=80),
        db.ForeignKey("user.username"), nullable=False)
    message = db.Column("message", db.String(length=1500), nullable=False)
    dateadded = db.Column("dateadded", db.DateTime, nullable=False, default=datetime.now)
    removed = db.Column("removed", db.Integer, nullable=False, default=0)

    def serialize(self):
        return {
            "id":self.id_,
            "user_from":self.user_from,
            "message":self.message,
            "dateadded":self.dateadded,
            "removed":self.removed
        }
