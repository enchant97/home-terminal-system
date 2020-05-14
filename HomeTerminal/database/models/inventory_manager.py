"""
contains the inventory manager models
"""
from .base import Base, db


class Location(Base):
    __tablename__ = "im_locations"
    name = db.Column(db.String(length=150), unique=True, nullable=False)
    comment = db.Column(db.String(length=1500))

class Type(Base):
    __tablename__ = "im_types"
    name = db.Column(db.String(length=150), unique=True, nullable=False)

class Box(Base):
    __tablename__ = "im_boxes"
    name = db.Column(db.String(length=150), unique=True)
    loc_id = db.Column(db.Integer, db.ForeignKey("im_locations.id"), nullable=False)

    location = db.relation(Location, backref=__tablename__)


class Item(Base):
    __tablename__ = "im_items"
    name = db.Column(db.String(length=150), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey("im_types.id"), nullable=False)
    box_id = db.Column(db.Integer, db.ForeignKey("im_boxes.id"), nullable=False)
    in_box = db.Column(db.Boolean, default=True, nullable=False)

    type_ = db.relation(Type, backref=__tablename__)
    box = db.relation(Box, backref=__tablename__)
