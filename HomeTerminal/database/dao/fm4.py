from datetime import datetime, timedelta

from ..database import db
from ..models.fm4 import FM4_Category, FM4_Item
from .exceptions import RowDoesNotExist


def get_fm4_expiring(days=7, count=False):
    """
    Will return the number of items that
    will expire between the days given

    args:
        days: used to compare between
        expiredate lessthan or equal to days after
        count: whether it should return the number of or the items
    """
    days_after = datetime.now() + timedelta(days=days)
    items = FM4_Item.query.filter(FM4_Item.expire_date <= days_after).filter_by(removed=0)
    if count:
        return items.count()
    return items.all()

def get_fm4_report(category=None, removed=0):
    """
    returns FM4_Item obj from database

    args:
        category : category to filter by, if None will return all
        removed : allows to display removed entries
    """
    if category:
        items = FM4_Item.query.filter_by(categoryname=category, removed=removed)
    else:
        items = FM4_Item.query.filter_by(removed=removed)

    return items.order_by(FM4_Item.expire_date).all()

def get_fm4_categories(removed=0):
    """
    returns all the fm4 categories
    """
    return FM4_Category.query.filter_by(removed=removed).all()

def get_fm4_item(id_):
    """
    returns the fm4 item,
    or raises RowDoesNotExist
    """
    fm_item = FM4_Item.query.filter_by(id_=id_).first()
    if not fm_item:
        raise RowDoesNotExist("Row with id {id_} does not exist")
    return fm_item

def edit_fm4_item(name, categoryname, quantity, expire=None, removed=0, id_=None):
    """
    Used to create an fm4 Item or edit an existing one,
    returns the edited item
    """
    if id_:
        fm_item = get_fm4_item(id_)
    else:
        fm_item = fm_item()

    fm_item.name = name
    if expire:
        fm_item.expire_date = expire
    if not FM4_Category.query.filter_by(name=categoryname).scalar():
        # create category if it does not exist
        db.session.add(FM4_Category(name=categoryname))
        db.session.commit()
    fm_item.categoryname = categoryname
    fm_item.quantity = quantity
    fm_item.removed = removed

    db.session.add(fm_item)
    db.session.commit()
    return fm_item
