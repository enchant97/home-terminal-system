from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from ..database import db
from .base import BaseNoUpdate


# source: https://dev.to/kaelscion/authentication-hashing-in-sqlalchemy-1bem
class User(UserMixin, BaseNoUpdate):
    """
    Stores info about users
    """
    __tablename__ = "users"
    username = db.Column("username", db.String(length=80))
    password_hash = db.Column(db.String(length=512), nullable=False)
    lastlogin = db.Column("lastlogin", db.DateTime, nullable=False, default=datetime.utcnow)
    birthday = db.Column("birthday", db.DateTime, nullable=False)

    def set_password(self, new_password):
        """
        Sets a new password and hashes it
        """
        self.password_hash = generate_password_hash(new_password, method='sha512')

    def check_password(self, the_password):
        """
        Whether the given password matches,
        return True or False
        """
        return check_password_hash(self.password_hash, the_password)

    def get_id(self):
        """
        returns the user id,
        override for UserMixin
        """
        return self.id_

    def __repr__(self):
        return f"username={self.username}, lastlogin={self.lastlogin}"


class User_Settings(db.Model):
    """
    Where user settings are stored.
    Each user should have one of these
    """
    __tablename__ = "user_settings"
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    fm_notif = db.Column(db.Boolean, nullable=False, default=False)
    rem_notif = db.Column(db.Boolean, nullable=False, default=False)
    mess_notif = db.Column(db.Boolean, nullable=False, default=False)
    removed = db.Column(db.Boolean, nullable=False, default=False)

    user = db.relation(User, backref=__tablename__)

    def serialize(self):
        return {
            "fm_notif":self.fm_notif,
            "rem_notif":self.rem_notif,
            "mess_notif":self.mess_notif
        }


class Api_Key(db.Model):
    """
    Stores api keys and registers each owner
    """
    __tablename__ = "api_keys"
    key = db.Column("key", db.String(length=128), primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True)
    removed = db.Column(db.Boolean, nullable=False, default=False)

    user = db.relation(User, backref=__tablename__)


class Message(BaseNoUpdate):
    __tablename__ = "messages"
    user_id_from = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    message = db.Column("message", db.String(length=1500), nullable=False)
    dateadded = db.Column("dateadded", db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relation(User, backref=__tablename__)

    def serialize(self):
        return {
            "id":self.id_,
            "user_from":self.user.username,
            "message":self.message,
            "dateadded":self.dateadded,
            "removed":self.removed
        }
