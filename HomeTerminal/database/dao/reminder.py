"""
functions for abstracting the reminder models
"""
from ..dao.exceptions import RowDoesNotExist
from ..database import db
from ..models.reminder import Reminder, Reminder_Type
from ..models.user import User


def new_reminder(content, user_for, type_name, is_priority=False, removed=False):
    """
    adds new reminder and returns the reminder obj

    args:
        content: the content/message of the reminder
        user_for: the username the notification is for or None
        type_name: the type name
        is_priority: whether it is priority
        removed: whether the entry is marked for removal
    """
    the_reminder = Reminder()
    the_reminder.content = content
    the_reminder.removed = bool(removed)
    if user_for:
        the_user = User.query.filter_by(username=user_for.lower()).first()
        if not the_user:
            raise RowDoesNotExist(f"username {user_for} does not exist")
        the_reminder.user_id_for = the_user.id_
    the_reminder.is_priority = bool(is_priority)

    # add or get reminder_type id
    r_type = Reminder_Type.query.filter_by(type_name=type_name.lower()).first()
    if not r_type:
        # if reminder type does not exist create one
        r_type = Reminder_Type(type_name=type_name.lower())
        db.session.add(r_type)
        db.session.commit()
    the_reminder.reminder_type_id = r_type.id_

    db.session.add(the_reminder)
    db.session.commit()
    return the_reminder

def remove_reminder(reminder_id, is_removed=True):
    """
    Allows for removing a reminder,
    also giving the option to 'undo'

    args:
        reminder_id : the reminder id
        is_removed : mark the entry for removal or undo
    """
    reminder = Reminder.query.filter_by(id_=reminder_id).first()
    if not reminder:
        raise RowDoesNotExist(f"row with id {reminder_id} does not exist")
    reminder.removed = is_removed
    db.session.add(reminder)
    db.session.commit()

def get_reminders(type_name=None, removed=False):
    if type_name:
        r_type = Reminder_Type.query.filter_by(type_name=type_name.lower()).first()
        return Reminder.query.filter_by(reminder_type_id=r_type.id_, removed=removed)
    return Reminder.query.filter_by(removed=removed)

def get_reminder_types(removed=False):
    """
    gets reminder types
    """
    return Reminder_Type.query.filter_by(removed=removed).all()
