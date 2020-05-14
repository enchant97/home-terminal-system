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
