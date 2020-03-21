from datetime import datetime

from .base import Base, db


class Category(Base):
    """
    Contains the category row
    """
    __tablename__ = "fm_categories"
    name = db.Column(db.String(length=128), unique=True)


class Item(Base):
    """
    contains the item row
    """
    __tablename__ = "fm_items"
    name = db.Column(db.String(length=128), nullable=False)
    expire_date = db.Column(db.DateTime, nullable=False)
    category_id = db.Column(
        db.Integer,
        db.ForeignKey("fm_categories.id"), nullable=False)
    quantity = db.Column("quantity", db.Integer, nullable=False)

    category = db.relation(Category, backref=__tablename__)

    def get_day_first_date(self):
        """
        returns expire_date as format '%d-%m-%Y'
        """
        return datetime.strftime(self.expire_date, "%d-%m-%Y")
