from uuid import UUID

from ..database import db
from ..models.dashboard import Shortcut, Widget
from .exceptions import AlreadyMarkedAsRemoved, RowDoesNotExist


def get_shortcuts(removed=False):
    """
    returns all shortcuts
    """
    return Shortcut.query.filter_by(removed=removed).all()

def get_shortcuts_by_ids(*ids):
    """
    returns the shortcuts that have the specific id's given

        :param *ids: the ids to filter by
    """
    return Shortcut.query.filter_by(removed=False).filter(Shortcut.id_.in_(ids)).all()

def get_shortcut(shortcut_id: int) -> Shortcut:
    """
    returns a specific shortcut row

        :param shortcut_id: the shortcut id
    """
    return Shortcut.query.filter_by(id_=shortcut_id).all()

def new_shortcut(name: str, url_endpoint: str, **url_variables) -> Shortcut:
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

def add_widget(user_id: int, widget_uuid: UUID, id_to_replace=None) -> Widget:
    """
    adds a new widget row

        :param user_id: the user id from the User model
        :param widget_uuid: the widget uuid, each widget in
                            the app has one
        :param id_to_replace: the id of the widget to place above,
                              if None will place at root
        :return: the created widget row
    """
    #TODO: allow for adding below(after) other widgets not just above(before)
    new_widget = Widget(user_id=user_id, widget_uuid=widget_uuid)
    db.session.add(new_widget)
    db.session.commit()

    # get row to replace
    row_to_replace = None
    if id_to_replace is None:
        # find the root, and set as row to replace
        row_to_replace = Widget.query.filter_by(
            left_widget_id=None,
            removed=False,
            user_id=user_id).filter(Widget.id_!=new_widget.id_).first()
        if not row_to_replace:
            # no root
            return new_widget
    else:
        # find the row to replace with given id
        row_to_replace = Widget.query.filter_by(
            id_=id_to_replace,
            removed=False,
            user_id=user_id).first()

    if not row_to_replace:
        raise RowDoesNotExist(f"Widget row with id of {id_to_replace} does not exist")

    if row_to_replace.left_widget_id:
        # if the widget is not a root
        row_to_replace_left = Widget.query.filter_by(id_=row_to_replace.left_widget_id).first()
        new_widget.left_widget_id = row_to_replace_left.id_
        row_to_replace_left.right_widget_id = new_widget.id_

    row_to_replace.left_widget_id = new_widget.id_
    new_widget.right_widget_id = row_to_replace.id_

    db.session.commit()
    return new_widget

def update_widget_setting(widget_id: int, new_settings):
    widget = Widget.query.filter_by(id_=widget_id).first()
    if not widget:
        raise RowDoesNotExist(f"widget row with the id does not exist, {widget_id}")
    widget.widget_settings = new_settings
    db.session.commit()
    return widget

def _reshuffle_widgets(widget: Widget):
    """
    will 'reshuffle' the widgets to the left
    and right of the given widget,will **not** commit changes

        :param widget: the widget that is going to be removed
    """
    if widget.left_widget_id and widget.right_widget_id:
        # update both the right and left widget id's
        left_widget = Widget.query.filter_by(id_=widget.left_widget_id).first()
        right_widget = Widget.query.filter_by(id_=widget.right_widget_id).first()
        left_widget.right_widget_id = right_widget.id_
        right_widget.left_widget_id = left_widget.id_

    elif widget.left_widget_id is None and widget.right_widget_id:
        # update only right widget
        right_widget = Widget.query.filter_by(id_=widget.right_widget_id).first()
        right_widget.left_widget_id = None

    elif widget.left_widget_id and widget.right_widget_id is None:
        # update only left widget
        left_widget = Widget.query.filter_by(id_=widget.left_widget_id).first()
        left_widget.right_widget_id = None

def remove_widget(widget_id):
    """
    remove a widget, while still allowing all widgets to be connected still

        :param widget_id: the widget id to remove
    """
    widget_to_remove = Widget.query.filter_by(id_=widget_id).first()

    # certain checks that will cause further updates to not work
    if not widget_to_remove:
        raise RowDoesNotExist(f"row does not exist with id {widget_id}")
    if widget_to_remove.removed:
        raise AlreadyMarkedAsRemoved(f"row already removed with id {widget_id}")

    _reshuffle_widgets(widget_to_remove)

    # if widget has no left or right id then just delete it
    widget_to_remove.removed = True

    db.session.commit()

def move_widget(widget_id: int, id_to_replace: int, user_id: int):
    """
    allows for moving widgets around

        :param widget_id: widget that will be moving
        :param id_to_replace: the widget to 'replace'
        :param user_id: the user id
    """
    #TODO: allow for adding below(after) other widgets not just above(before)
    if widget_id == id_to_replace:
        raise ValueError("widget_id and id_to_replace cannot be the same")

    # get the widgets
    widget_to_move = Widget.query.filter_by(id_=widget_id, user_id=user_id).first()
    widget_to_be_replaced = Widget.query.filter_by(id_=id_to_replace, user_id=user_id).first()

    # check whether they exist
    if not widget_to_move or not widget_to_be_replaced:
        raise RowDoesNotExist("row does not exist with that id")

    # change the widgets around the widget to move
    _reshuffle_widgets(widget_to_move)

    # change the widgets around where the widget will be
    if widget_to_be_replaced.left_widget_id:
        left_widget = Widget.query.filter_by(id_=widget_to_be_replaced.left_widget_id, user_id=user_id).first()
        left_widget.right_widget_id = widget_to_move.id_

    widget_to_move.left_widget_id = widget_to_be_replaced.left_widget_id
    widget_to_be_replaced.left_widget_id = widget_to_move.id_
    widget_to_move.right_widget_id = widget_to_be_replaced.id_

    db.session.commit()

def get_widget(user_id: int, widget_id: int, removed=False) -> Widget:
    """
    get a widget from database

        :param user_id: id of the user
        :param widget_id: id of the widget
        :param removed: whether to include removed entries
        :return: a Wiget object
    """
    return Widget.query.filter_by(id_=widget_id, user_id=user_id, removed=removed).first()

def get_dashboard_widget_order(user_id):
    """
    returns the users dashboard widgets order (root first)

        :param user_id: the user id
        :return: generator which will yield each row
    """
    # find the users root widget, if they have one
    root_widget = Widget.query.filter_by(
        user_id=user_id, removed=False, left_widget_id=None).first()
    if root_widget:
        yield root_widget
        # make sure there are more widgets after
        if root_widget.right_widget_id:
            curr_parent = root_widget.right_widget
            while curr_parent:
                # keep yielding each widget in order
                yield curr_parent
                curr_parent = curr_parent.right_widget

def delete_removed():
    """
    delete the rows that are marked as removed
    """
    for row in Shortcut.query.filter_by(removed=True).all():
        db.session.delete(row)
    for row in Widget.query.filter_by(removed=True).all():
        db.session.delete(row)
    db.session.commit()
