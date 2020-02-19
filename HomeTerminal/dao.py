import logging
from datetime import datetime

from .models import (Api_Key, Homework_Main, Message, Table_Updates, User,
                     User_Settings, db)
from .utils import hash_str


class RowAlreadyExists(Exception):
    pass


class AlreadyUpToDate(Exception):
    pass


def mark_table_updated(table_name):
    """
    Change a the update time table row,
    uses utc time

    args:
        just_creating : if the row already exists will not update the datetime
    """
    if Table_Updates.query.filter_by(table_name=table_name).scalar():
        new_row = Table_Updates.query.filter_by(table_name=table_name)
        new_row.last_updated = datetime.utcnow()
    else:
        new_row = Table_Updates(table_name=table_name)
    db.session.add(new_row)
    db.session.commit()

def get_last_updated(table_name):
    """
    Returns the last time the table was updated,
    returns a datetime obj
    """
    sel_row = Table_Updates.query.filter_by(table_name=table_name).first()
    if sel_row:
        return sel_row.last_updated

def try_login_user(username, password):
    """
    returns user obj and sets last login date, if password and username match
    """
    the_user = User.query.filter_by(username=username, password=hash_str(password)).first()
    if the_user:
        the_user.lastlogin = datetime.now()
        db.session.add(the_user)
        db.session.commit()
        logging.debug(f"User Logged In {username}")
        return the_user

def new_account(username, password, birthday: datetime, ignore_duplicate=False):
    """
    creates a new account in the database
    """
    if User.query.filter_by(username=username).scalar():
        # if the username already exists
        if not ignore_duplicate:
            raise RowAlreadyExists(f"username already exists: {username}")
        else:
            return
    password = hash_str(password)

    new_user = User(username=username.lower(), password=password, birthday=birthday)
    db.session.add(new_user)
    db.session.add(User_Settings(username=username))
    db.session.commit()

def change_user_password(username, new_password, old_password):
    """
    returns user obj if password change was success
    """
    old_password = hash_str(old_password)
    new_password = hash_str(new_password)

    the_user = User.query.filter_by(username=username, password=old_password).first()

    if the_user:
        the_user.password = new_password
        db.session.add(the_user)
        db.session.commit()
        return the_user

def new_message(user_from, message):
    """
    adds a new message into database,
    returns message obj on success
    """
    the_message = Message(user_from=user_from, message=message)
    db.session.add(the_message)
    db.session.commit()
    return the_message

def check_api_key(api_key):
    """
    Checks whether the api key given is valid
    """
    if Api_Key.query.filter_by(key=api_key).scalar():
        return True
    else:
        return False

def get_messages(removed=0, last_updated=None):
    """
    Returns the messages,
    if last_updated is datetime will raise
    AlreadyUpToDate if it is already up to date

    args:
        removed : whether to select removed entries or not
        last_updated : datetime obj or '%Y-%m-%d %H:%M:%S.%f'
    """
    if last_updated:
        last_updated = datetime.strptime(last_updated, "%Y-%m-%d %H:%M:%S.%f")
        #TODO: seperate this into a function?
        db_updated = get_last_updated(Message.__tablename__)
        if db_updated:
            if db_updated <= last_updated:
                raise AlreadyUpToDate()

    return Message.query.filter_by(removed=removed).all()

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
