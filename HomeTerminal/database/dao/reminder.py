"""
functions for abstracting the reminder models
"""
from datetime import datetime, timedelta

from sqlalchemy import and_, or_

from ..dao.exceptions import RowDoesNotExist
from ..database import db
from ..models.reminder import Reminder, Reminder_Task, Reminder_Type
from ..models.user import User


def new_reminder(content, type_name, is_priority=False, datedue=None, user_for_id=None) -> Reminder:
    """
    adds new reminder and returns the reminder obj

        :param content: the content/message of the reminder
        :param type_name: the type name
        :param is_priority: whether it is priority, defaults to False
        :param datedue: when the reminder should alert, defaults to None
        :param user_for_id: the id of the user the reminder is for or None, defaults to None
        :return: the created reminder obj
    """
    #TODO use id for type instead
    if user_for_id is not None:
        if User.query.filter_by(id_=user_for_id).scalar() is None:
            raise RowDoesNotExist(f"username {user_for_id} does not exist")

    the_reminder = Reminder(
        content=content,
        is_priority=is_priority,
        datedue=datedue,
        user_id_for=user_for_id
    )

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

def new_reminder_task(reminder_id: int, name: str, *args) -> Reminder_Task:
    """
    adds a new reminder task and returns it on creation

        :param reminder_id: the reminder id row
        :param name: the name of the task
        :param *args: extra names to make multiple tasks
        :return: yields each created reminder task obj
    """
    if Reminder.query.filter_by(id_=reminder_id).scalar() is None:
        raise RowDoesNotExist(f"reminder row does not exist {reminder_id}")

    new_task = Reminder_Task(
        reminder_id=reminder_id,
        name=name
    )
    db.session.add(new_task)
    for extra_name in args:
        # add extra tasks that were given
        db.session.add(
            Reminder_Task(
                reminder_id=reminder_id,
                name=extra_name
            )
        )
    db.session.commit()
    return new_task

def remove_reminder_task(reminder_task_id: int, is_removed=True):
    """
    marks a reminder task as removed

    :param reminder_task_id: the reminder task id
    :param is_removed: allow for unmarking row a removed, defaults to True
    """
    task = Reminder_Task.query.filter_by(id_=reminder_task_id).first()
    task.removed = is_removed
    db.session.commit()

def remove_reminder(reminder_id, is_removed=True) -> Reminder:
    """
    Allows for removing a reminder,
    also giving the option to 'undo'

        :param reminder_id: the reminder id
        :param is_removed: mark the entry for removal or undo, defaults to True
        :return: the reminder obj that was marked as removed
    """
    reminder = Reminder.query.filter_by(id_=reminder_id).first()
    if not reminder:
        raise RowDoesNotExist(f"row with id {reminder_id} does not exist")
    reminder.removed = is_removed

    Reminder_Task.query.filter_by(reminder_id=reminder_id).update(dict(removed=is_removed))
    db.session.commit()
    return reminder

def get_reminders(only_first=False, **filters):
    """
    list of each reminder row that match given filters
    if only_first is True it only return Reminder obj

        :param only_first: whether to only return first row, defaults to False
        :param **filters: filters for the query
        :return: reminder row obj or yield 1 at a time
    """
    query = Reminder.query.filter_by(**filters)
    if only_first:
        return query.first()
    return query.all()

def get_reminder_tasks(**filters):
    """
    returns all reminder tasks,
    using provided filters

        :return: the reminder task rows
    """
    return Reminder_Task.query.filter_by(**filters).all()

def get_reminder_types(removed=False):
    """
    gets reminder types

        :param removed: whether to select removed entries, defaults to False
    """
    return Reminder_Type.query.filter_by(removed=removed).all()

def get_reminders_due(user_id: int, include_general=True, only_count=False, days=2):
    """
    filter by reminders that are due,
    days var allows for reminders to appear early

        :param user_id: the user id to search for
        :param personal_only: include general reminders, defaults to True
        :param only_count: whether to return just count of items, defaults to False
        :param days: allow for before days to be selected
    """
    days_after = datetime.now() + timedelta(days=days)
    query = Reminder.query.filter_by(removed=False)
    if include_general:
        query = query.filter(and_(
            Reminder.datedue <= days_after,
            or_(Reminder.user_id_for == user_id, Reminder.user_id_for == None)))
    else:
        query = query.filter(and_(Reminder.datedue <= days_after, Reminder.user_id_for == user_id))
    if only_count:
        return query.count()
    return query.all()

def delete_removed():
    """
    delete the rows that are marked as removed
    """
    Reminder_Task.query.filter_by(removed=True).delete()
    Reminder.query.filter_by(removed=True).delete()
    Reminder_Type.query.filter_by(removed=True).delete()
    db.session.commit()
