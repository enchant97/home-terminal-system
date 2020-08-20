from ..database import db
from ..models.dashboard import Shortcut, User_Shortcut


def get_shortcuts(removed=False):
    """
    returns all shortcuts
    """
    return Shortcut.query.filter_by(removed=removed).all()

def get_user_shortcuts(user_id: int, removed=False):
    """
    returns user shortcuts for the specified user_id
    """
    return User_Shortcut.query.filter_by(
        user_id=user_id, removed=removed).order_by(User_Shortcut.priority).all()

def remove_user_shortcuts(user_id: int):
    """
    removes all entries with the given user_id,
    returns the number of rows deleted
    """
    rows_deleted = User_Shortcut.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    return rows_deleted

def new_shortcut(name: str, url_endpoint: str, **url_variables):
    """
    adds a new shortcut using provided values,
    returns the created shortcut
    """
    the_shortcut = Shortcut(
        name=name,
        url_endpoint=url_endpoint,
        url_variables=url_variables
    )
    db.session.add(the_shortcut)
    db.session.commit()
    return the_shortcut

def update_user_shortcut(user_id: int, shortcut_id: int, priority: int):
    """
    adds a new user shortcut using provided values,
    if it already exists changes updates the priority,
    returns the created shortcut
    """
    the_user_shortcut = User_Shortcut.query.filter_by(user_id=user_id, shortcut_id=user_id).first()

    if not the_user_shortcut:
        the_user_shortcut = User_Shortcut()

    the_user_shortcut.user_id = user_id
    the_user_shortcut.shortcut_id = shortcut_id
    the_user_shortcut.priority = priority

    db.session.add(the_user_shortcut)
    db.session.commit()
    return the_user_shortcut

def delete_removed():
    """
    delete the rows that are marked as removed
    """
    for row in Shortcut.query.filter_by(removed=True).all():
        db.session.delete(row)
    for row in User_Shortcut.query.filter_by(removed=True).all():
        db.session.delete(row)
    db.session.commit()
