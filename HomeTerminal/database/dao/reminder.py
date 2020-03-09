from ..dao.exceptions import RowDoesNotExist
from ..database import db
from ..models.reminder import Reminder, Reminder_Type


def new_reminder(content, user_for, type_name, is_priority, removed):
    """
    adds new reminder and returns the reminder obj
    """
    the_reminder = Reminder()
    the_reminder.content = content
    the_reminder.removed = bool(removed)
    if user_for:
        the_reminder.user_for = user_for.lower()
    the_reminder.is_priority = bool(is_priority)

    # add or get reminder_type id
    r_type = Reminder_Type.query.filter_by(type_name=type_name.lower()).first()
    if not r_type:
        # if reminder type does not exist create one
        r_type = Reminder_Type(type_name=type_name.lower())
        db.session.add(r_type)
        db.session.commit()
    the_reminder.reminder_type = r_type.id_

    db.session.add(the_reminder)
    db.session.commit()
    return the_reminder

def remove_reminder(reminder_id, is_removed=True):
    """
    Allows for removing a reminder,
    also giving the option to 'undo'
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
        return Reminder.query.filter_by(reminder_type=r_type.id_, removed=removed)
    return Reminder.query.filter_by(removed=removed)

def get_reminder_types(removed=False):
    """
    gets reminder types
    """
    return Reminder_Type.query.filter_by(removed=removed).all()
