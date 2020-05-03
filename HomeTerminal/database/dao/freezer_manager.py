from datetime import datetime, timedelta

from ..database import db
from ..models.freezer_manager import Category, Item
from .exceptions import RowDoesNotExist


def get_fm4_expiring(days=7, count=False):
    """
    returns the number of items that
    will expire between the days given

    args:
        days: used to compare between
        expire date less than or equal to days after
        count: whether it should return the number of or the items
    """
    #TODO: use utc now instead
    days_after = datetime.now() + timedelta(days=days)
    items = Item.query.filter(Item.expire_date <= days_after).filter_by(removed=False)
    if count:
        return items.count()
    return items.all()

def get_fm4_report(category=None, removed=False):
    """
    returns FM4_Item obj from database

    args:
        category : category to filter by, if None will return all
        removed : allows to display removed entries
    """
    if category:
        the_category = Category.query.filter_by(name=category).first()
        if not the_category:
            raise RowDoesNotExist(f"category name {category} does not exist")
        items = Item.query.filter_by(category_id=the_category.id_, removed=removed)
    else:
        items = Item.query.filter_by(removed=removed)

    return items.order_by(Item.expire_date).all()

def get_fm4_categories(removed=False):
    """
    returns all the fm4 categories
    """
    return Category.query.filter_by(removed=removed).all()

def get_fm4_item(id_):
    """
    returns the fm4 item,
    or raises RowDoesNotExist
    """
    fm_item = Item.query.filter_by(id_=id_).first()
    if not fm_item:
        raise RowDoesNotExist(f"Row with id {id_} does not exist")
    return fm_item

def edit_fm4_item(name, categoryname, quantity, expire=None, removed=False, id_=None):
    """
    Used to create an fm4 Item or edit an existing one,
    returns the edited item
    """
    if id_:
        fm_item = get_fm4_item(id_)
    else:
        fm_item = Item()

    fm_item.name = name
    if expire:
        fm_item.expire_date = expire

    if not Category.query.filter_by(name=categoryname).scalar():
        # create category if it does not exist
        the_category = Category(name=categoryname)
        db.session.add(the_category)
        db.session.commit()
    else:
        the_category = Category.query.filter_by(name=categoryname).first()
        the_category.update_last_updated()

    fm_item.category_id = the_category.id_
    fm_item.quantity = quantity
    fm_item.removed = removed

    db.session.add(fm_item)
    db.session.commit()
    return fm_item
