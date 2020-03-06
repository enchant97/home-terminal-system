from datetime import datetime

from ..database import db


class FM4_Category(db.Model):
    __tablename__ = "fm4_category"
    name = db.Column("name", db.String(length=128), primary_key=True)
    removed = db.Column("removed", db.Integer, nullable=False, default=0)

class FM4_Item(db.Model):
    __tablename__ = "fm4_item"
    id_ = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(length=128), nullable=False)
    expire_date = db.Column("expire_date", db.DateTime, nullable=False)
    categoryname = db.Column(
        "category", db.String(length=128),
        db.ForeignKey("fm4_category.name"), nullable=False)
    quantity = db.Column("quantity", db.Integer, nullable=False)
    removed = db.Column("removed", db.Integer, nullable=False, default=0)

    def get_day_first_date(self):
        """
        returns expire_date as format '%d-%m-%Y'
        """
        return datetime.strftime(self.expire_date, "%d-%m-%Y")
