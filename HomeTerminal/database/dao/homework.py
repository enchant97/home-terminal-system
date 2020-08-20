from datetime import datetime

from ..database import db
from ..models.homework import Main, Task
from .exceptions import AlreadyUpToDate


def get_homework_ordered(removed=False, last_updated=None):
    """
    Returns the homework,
    if last_updated is datetime will raise
    AlreadyUpToDate if it is already up to date

        :param removed: whether to select removed entries or not
        :param last_updated: datetime obj or '%Y-%m-%d %H:%M:%S.%f'
    """
    if last_updated:
        if not isinstance(datetime, last_updated):
            # if the last_updated was a string try to convert
            last_updated = datetime.strptime(last_updated, "%Y-%m-%d %H:%M:%S.%f")
        last_hw = Main.query.filter_by(removed=removed).order_by(Main.last_updated.desc()).first()
        if last_hw:
            if last_hw.last_updated <= last_updated:
                raise AlreadyUpToDate()

    return Main.query.filter_by(removed=removed).order_by(Main.datedue).all()

def get_homework_tasks(hw_id, removed=False):
    """
    returns the homework tasks related to the given homework id

        :param hw_id: the homework main id
        :param removed: whether to select removed entries or not
    """
    return Task.query.filter_by(removed=removed, hw_id=hw_id).all()

def edit_homework(message, datedue, removed=False, id_=None):
    """
    Allows for editing or adding a new homework,
    editing is not implemented,
    returns a Homework_Main obj

        :param message: the message for the homework
        :param datedue: datetime obj for when it is due
        :param removed: whether entries should be marked for removal
        :param id_: the id of the homework if editing
    """
    if id_:
        #TODO: implement
        raise NotImplementedError("edit homework not available :(")
    homework = Main()

    homework.message = message
    homework.datedue = datedue
    homework.removed = removed

    db.session.add(homework)
    db.session.commit()
    return homework

def edit_homework_task(content, hw_id, removed=False, id_=None):
    """
    Allows for editing or adding a new homework task,
    editing is not implemented,
    returns Homework_Task obj/s

        :param content: the task content, if multiple tasks
                        need to be added send list/tuple
        :param hw_id: id for the Homework_Main it relates to
        :param removed: whether entries should be marked for removal
        :param id_: the id of the homework task if editing
    """
    if id_:
        #TODO: implement
        raise NotImplementedError("edit homework task not available :(")

    if isinstance(content, (list, tuple)):
        tasks = []
        for mess in content:
            task = Task(content=mess, hw_id=hw_id, removed=removed)
            tasks.append(task)
        for task in tasks:
            db.session.add(task)
        db.session.commit()
        return tasks
    task = Task(content=content, hw_id=hw_id, removed=removed)
    db.session.add(task)
    db.session.commit()
    return task

def mark_homework_for_removal(id_, removed=True):
    """
    marks tasks and homework for removal

        :param id_: the id of the hw entry
    """
    #TODO: implement RowDoesNotExist error
    Main.query.filter_by(id_=id_).update(dict(removed=removed))
    Task.query.filter_by(hw_id=id_).update(dict(removed=removed))
    db.session.commit()

def delete_removed():
    """
    delete the rows that are marked as removed
    """
    for row in Main.query.filter_by(removed=True).all():
        db.session.delete(row)
    for row in Task.query.filter_by(removed=True).all():
        db.session.delete(row)
    db.session.commit()
