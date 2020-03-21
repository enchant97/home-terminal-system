"""
contains the photo manager models
"""
from .base import Base, db
from .user import User


class MainLocation(Base):
    """
    Where the main location data is stored
    """
    __tablename__ = "pd_mainlocs"
    name = db.Column(db.String(length=500), unique=True)


class SubLocation(Base):
    """
    Where the sub location data is stored
    """
    __tablename__ = "pd_sublocs"
    name = db.Column(db.String(length=500), nullable=False, unique=True)
    main_loc_id = db.Column(db.Integer, db.ForeignKey("pd_mainlocs.id"), nullable=False)
    lat = db.Column(db.Float(precision=10, decimal_return_scale=None), nullable=False)
    lng = db.Column(db.Float(precision=10, decimal_return_scale=None), nullable=False)

    main_location = db.relation(MainLocation, backref=__tablename__)

    def serialize(self):
        return {
            "name":self.name,
            "main_name":self.main_location.name
        }


class FullEvent(Base):
    """
    Where the full event data is stored
    """
    __tablename__ = "pd_fullevents"
    subloc_id = db.Column(db.Integer, db.ForeignKey("pd_sublocs.id"), nullable=False)
    date_taken = db.Column(db.DateTime, nullable=False)
    notes = db.Column("notes", db.String(length=2000), nullable=False)

    sub_location = db.relation(MainLocation, backref=__tablename__)


class UserEvent(Base):
    """
    Where the user event data is stored
    """
    __tablename__ = "pd_userevents"
    full_event_id = db.Column(db.Integer, db.ForeignKey("pd_fullevents.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    user = db.relation(User, backref=__tablename__)
