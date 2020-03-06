from datetime import datetime

from ..database import db
from ..models.hwm import Homework_Main, Homework_Task
from .exceptions import AlreadyUpToDate
from .other import get_last_updated


def get_homework_ordered(removed=0, last_updated=None):
    """
    Returns the homework,
    if last_updated is datetime will raise
    AlreadyUpToDate if it is already up to date

    args:
        removed : whether to select removed entries or not
        last_updated : datetime obj or '%Y-%m-%d %H:%M:%S.%f'
    """
    if last_updated:
        last_updated = datetime.strptime(last_updated, "%Y-%m-%d %H:%M:%S.%f")
        db_updated = get_last_updated(Homework_Main.__tablename__)
        if db_updated:
            if db_updated <= last_updated:
                raise AlreadyUpToDate()
    return Homework_Main.query.filter_by(removed=removed).order_by(Homework_Main.datedue).all()

def get_homework_tasks(hw_id, removed=0):
    """
    returns the homework tasks related to the given homework id
    """
    return Homework_Task.query.filter_by(removed=removed, hw_id=hw_id).all()

def edit_homework(message, datedue, removed=0, id_=None):
    """
    Allows for editing or adding a new homework,
    editing is not implemented,
    returns a Homework_Main obj

    args:
        message: the message for the homework
        datedue: datetime obj for when it is due
        removed: whether entries should be marked for removal
        id_: the id of the homework if editing
    """
    if id_:
        #TODO: implement
        raise NotImplementedError("edit homework not available :(")
    else:
        homework = Homework_Main()

    homework.message = message
    homework.datedue = datedue
    homework.removed = removed

    db.session.add(homework)
    db.session.commit()
    return homework

def edit_homework_task(content, hw_id, removed=0, id_=None):
    """
    Allows for editing or adding a new homework task,
    editing is not implemented,
    returns Homework_Task obj/s

    args:
        content: the task content, if multiple tasks need to be added send list/tuple
        hw_id: id for the Homework_Main it relates to
        removed: whether entries should be marked for removal
        id_: the id of the homework task if editing
    """
    if id_:
        #TODO: implement
        raise NotImplementedError("edit homework task not available :(")
    if isinstance(content, (list, tuple)):
        tasks = []
        for mess in content:
            task = Homework_Task(content=mess, hw_id=hw_id, removed=removed)
            tasks.append(task)
        for task in tasks:
            db.session.add(task)
        db.session.commit()
        return tasks
    task = Homework_Task(content=content, hw_id=hw_id, removed=removed)
    db.session.add(task)
    db.session.commit()
    return task

def mark_homework_for_removal(id_):
    """
    removes the homework and all the tasks related to it
    """
    #TODO: implement RowDoesNotExist error
    Homework_Main.query.filter_by(id_=id_).update(dict(removed=1))
    Homework_Task.query.filter_by(hw_id=id_).update(dict(removed=1))
    db.session.commit()
