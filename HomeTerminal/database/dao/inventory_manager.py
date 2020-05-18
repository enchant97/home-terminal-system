"""
functions for abstracting the inventory manager models
"""

from ..dao.exceptions import RowAlreadyExists, RowDoesNotExist
from ..database import db
from ..models.inventory_manager import Box, Item, Location, Type


def new_location(name: str, comment: str = None):
    """
    adds new location
    and returns it when created
    """
    if db.session.query(Location.id_).filter_by(name=name).scalar() is not None:
        raise RowAlreadyExists(f"location name '{name}' already exists")
    new_loc = Location(name=name, comment=comment)
    db.session.add(new_loc)
    db.session.commit()
    return new_loc

def new_type(name: str):
    """
    adds new type
    and returns it when created
    """
    if db.session.query(Type.id_).filter_by(name=name).scalar() is not None:
        raise RowAlreadyExists(f"type name '{name}' already exists")
    new_type_row = Type(name=name)
    db.session.add(new_type_row)
    db.session.commit()
    return new_type_row

def new_box(loc_id: int, name: str = None):
    """
    adds new box
    and returns it when created
    """
    if db.session.query(Location.id_).filter_by(id_=loc_id).scalar() is None:
        raise RowDoesNotExist(f"location id '{loc_id}' does not exist")
    if db.session.query(Box.id_).filter_by(name=name).scalar() is not None:
        raise RowAlreadyExists(f"box name '{name}' already exists")
    new_box_row = Box(loc_id=loc_id, name=name)
    db.session.add(new_box_row)
    db.session.commit()
    return new_box_row

def new_item(name: str, box_id: int, quantity: int = 1, type_id: int = None, in_box: int = True):
    """
    adds new item
    and returns it when created
    """
    if db.session.query(Box.id_).filter_by(id_=box_id).scalar() is None:
        raise RowDoesNotExist(f"box id '{box_id}' does not exist")
    if type_id:
        if db.session.query(Type.id_).filter_by(id_=type_id).scalar() is None:
            raise RowDoesNotExist(f"type id '{type_id}' does not exist")
    new_item_row = Item(
        name=name, box_id=box_id,
        quantity=quantity, type_id=type_id, in_box=in_box
        )
    db.session.add(new_item_row)
    db.session.commit()
    return new_item_row

def edit_location(loc_id, **kwargs):
    """
    used to edit a location row
    args:
        loc_id : location id for what value to update
        **kwargs : values to update
    """
    location_row = Location.query.filter_by(id_=loc_id)
    if not location_row.count():
        raise RowDoesNotExist(f"location row id '{loc_id}' does not exist")
    location_row.update(kwargs)
    db.session.commit()
    return location_row

def edit_type(type_id, **kwargs):
    """
    used to edit a type row
    args:
        type_id : type id for what value to update
        **kwargs : values to update
    """
    type_row = Type.query.filter_by(id_=type_id)
    if not type_row.count():
        raise RowDoesNotExist(f"type row id '{type_id}' does not exist")
    type_row.update(kwargs)
    db.session.commit()
    return type_row

def edit_box(box_id, **kwargs):
    """
    used to edit a box row
    args:
        box_id : box id for what value to update
        **kwargs : values to update
    """
    box_row = Box.query.filter_by(id_=box_id)
    if not box_row.count():
        raise RowDoesNotExist(f"box row id '{box_id}' does not exist")
    box_row.update(kwargs)
    db.session.commit()
    return box_row

def edit_item(item_id, **kwargs):
    """
    used to edit a item row
    args:
        item_id : item id for what value to update
        **kwargs : values to update
    """
    item_row = Item.query.filter_by(id_=item_id)
    if not item_row.count():
        raise RowDoesNotExist(f"item row id '{item_id}' does not exist")
    item_row.update(kwargs)
    db.session.commit()
    return item_row

def get_type(first=False, **filters):
    """
    returns Type rows

    args:
        first: whether to return first entry only or multiple
        filters: other row columns to filter by
    """
    query = Type.query.filter_by(**filters)
    if first:
        return query.first()
    return query.all()

def get_locations(first=False, **filters):
    """
    returns Location rows

    args:
        first: whether to return first entry only or multiple
        filters: other row columns to filter by
    """
    query = Location.query.filter_by(**filters)
    if first:
        return query.first()
    return query.all()

def get_box(first=False, **filters):
    """
    returns Box rows

    args:
        first: whether to return first entry only or multiple
        filters: other row columns to filter by
    """
    query = Box.query.filter_by(**filters)
    if first:
        return query.first()
    return query.all()

def get_item(first=False, **filters):
    """
    returns Item rows

    args:
        first: whether to return first entry only or multiple
        filters: other row columns to filter by
    """
    query = Item.query.filter_by(**filters)
    if first:
        return query.first()
    return query.all()

def get_like_item_names(name, limit: int = None):
    """
    returns Items, using like
    comparison for item name

    args:
        name : name to match entries to
        limit : limit the selected rows to a certain amount
    """
    query = Item.query.filter(Item.name.like(name + "%"))
    if limit:
        return query.limit(limit).all()
    return query.all()
