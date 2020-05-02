"""
stores models for how the dashboard operates for each user
"""
from ..database import db
from .base import BaseNoUpdate


class Shortcut(BaseNoUpdate):
    """
    model to store the shortcuts
    """
    __tablename__ = "shortcuts"
    name = db.Column(db.String(length=500), nullable=False)
    url_endpoint = db.Column(db.Text, nullable=False)
    url_variables = db.Column(db.PickleType, nullable=False)

class User_Shortcut(BaseNoUpdate):
    """
    model to store the user shortcuts
    shown in the dashboard
    """
    __tablename__ = "user_shortcuts"
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    shortcut_id = db.Column(db.Integer, db.ForeignKey("shortcuts.id"), nullable=False)
    priority = db.Column(db.Integer, default=0, nullable=False)
    shortcut = db.relation(Shortcut, backref=__tablename__)
