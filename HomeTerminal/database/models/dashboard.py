"""
stores models for how the dashboard operates for each user
"""
from ...helpers.types import BinaryMsgPack, BinaryUUID4
from ..database import db
from .base import Base


class Shortcut(Base):
    """
    model to store the shortcuts
    """
    __tablename__ = "shortcuts"
    name = db.Column(db.String(length=500), nullable=False)
    url_endpoint = db.Column(db.Text, nullable=False)
    url_variables = db.Column(db.PickleType, nullable=False)


class Widget(Base):
    """
    model to store the user widgets,
    with included settings held in msgpack
    """
    __tablename__ = "widgets"
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    widget_uuid = db.Column(BinaryUUID4, nullable=False)
    widget_settings = db.Column(BinaryMsgPack)

    left_widget_id = db.Column(db.Integer, db.ForeignKey("widgets.id"))
    right_widget_id = db.Column(db.Integer, db.ForeignKey("widgets.id"))

    left_widget = db.relation(
        "Widget", remote_side="Widget.id_",
        foreign_keys="Widget.left_widget_id")
    right_widget = db.relation(
        "Widget", remote_side="Widget.id_",
        foreign_keys="Widget.right_widget_id")
