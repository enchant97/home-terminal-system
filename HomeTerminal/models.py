"""
Contains all the database stuff
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

# MAIN

class User(db.Model):
    """
    Stores info about users
    """
    __tablename__ = "user"
    username = db.Column("username", db.String(length=80), primary_key=True)
    password = db.Column("password", db.String(length=128), nullable=False)
    lastlogin = db.Column("lastlogin", db.DateTime, nullable=False, default=datetime.now)
    birthday = db.Column("birthday", db.DateTime, nullable=False)
    removed = db.Column("removed", db.Integer, nullable=False, default=0)

    def __repr__(self):
        return f"username={self.username}, lastlogin={self.lastlogin}"

class User_Settings(db.Model):
    """
    Where user settings are stored.
    Each user should have one of these
    """
    __tablename__ = "user_settings"
    username = db.Column("username", db.String(length=80), db.ForeignKey("user.username"), primary_key=True)
    fm_notif = db.Column("fm_notif", db.Integer, nullable=False, default=0)
    hwm_notif = db.Column("hwm_notif", db.Integer, nullable=False, default=0)
    mess_notif = db.Column("mess_notif", db.Integer, nullable=False, default=0)

class Api_Key(db.Model):
    """
    Stores api keys and registers each owner
    """
    __tablename__ = "api_key"
    key = db.Column("key", db.String(length=128), primary_key=True)
    owner = db.Column("owner", db.String(length=80), db.ForeignKey("user.username"), nullable=False)
    removed = db.Column("removed", db.Integer, nullable=False, default=0)

class Message(db.Model):
    __tablename__ = "message"
    id_ = db.Column("id", db.Integer, primary_key=True)
    user_from = db.Column("user_from", db.String(length=80), db.ForeignKey("user.username"), nullable=False)
    message = db.Column("message", db.String(length=1500), nullable=False)
    dateadded = db.Column("dateadded", db.DateTime, nullable=False, default=datetime.now)
    removed = db.Column("removed", db.Integer, nullable=False, default=0)

# FREEZER MANAGER

class FM4_Category(db.Model):
    __tablename__ = "fm4_category"
    name = db.Column("name", db.String(length=128), primary_key=True)
    removed = db.Column("removed", db.Integer, nullable=False, default=0)

class FM4_Item(db.Model):
    __tablename__ = "fm4_item"
    id_ = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(length=128), nullable=False)
    expire_date = db.Column("expire_date", db.DateTime, nullable=False)
    categoryname = db.Column("category", db.String(length=128), db.ForeignKey("fm4_category.name"), nullable=False)
    quantity = db.Column("quantity", db.Integer, nullable=False)
    removed = db.Column("removed", db.Integer, nullable=False, default=0)

    def get_day_first_date(self):
        """
        returns expire_date as format '%d-%m-%Y'
        """
        return datetime.strftime(self.expire_date, "%d-%m-%Y")

# HOMEWORK

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
            "datedue":self.get_day_first_date()
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

# PHOTO DATABASE

class PD1_MainLocation(db.Model):
    """
    Where the main location data is stored
    """
    __tablename__ = "pd1_mainloc"
    name = db.Column("name", db.String(length=500), primary_key=True)

class PD1_SubLocation(db.Model):
    """
    Where the sub location data is stored
    """
    __tablename__ = "pd1_subloc"
    name = db.Column("name", db.String(length=500), primary_key=True)
    main_name = db.Column("main_name", db.String(length=500), db.ForeignKey("pd1_mainloc.name"), nullable=False)
    lat = db.Column("lat", db.Float(precision=10, decimal_return_scale=None), nullable=False)
    lng = db.Column("lng", db.Float(precision=10, decimal_return_scale=None), nullable=False)

    def serialize(self):
        """

        """
        return {
            "name":self.name,
            "main_name":self.main_name
        }

class PD1_FullEvent(db.Model):
    """
    Where the full event data is stored
    """
    __tablename__ = "pd1_fullevent"
    id_ = db.Column("id", db.Integer, primary_key=True)
    subloc = db.Column("subloc", db.String(length=500), db.ForeignKey("pd1_subloc.name"), nullable=False)
    date_taken = db.Column("datetaken", db.DateTime, nullable=False)
    notes = db.Column("notes", db.String(length=2000), nullable=False)

class PD1_UserEvent(db.Model):
    """
    Where the user event data is stored
    """
    __tablename__ = "pd1_userevent"
    id_ = db.Column("id", db.Integer, primary_key=True)
    full_event = db.Column("fullevent", db.Integer, db.ForeignKey("pd1_fullevent.id"), nullable=False)
    username = db.Column("username", db.String(length=80), db.ForeignKey("user.username"), nullable=False)
