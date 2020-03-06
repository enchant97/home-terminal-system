import logging
from datetime import datetime

from ...utils import Notification, hash_str
from ..database import db
from ..models.hwm import Homework_Main
from ..models.user import Api_Key, Message, User, User_Settings
from .exceptions import AlreadyUpToDate, RowAlreadyExists, RowDoesNotExist
from .fm4 import get_fm4_expiring
from .other import get_last_updated


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
    creates a new account in the database,
    returns the User obj
    """
    if User.query.filter_by(username=username).scalar():
        # if the username already exists
        if not ignore_duplicate:
            raise RowAlreadyExists(f"username already exists: {username}")
        return None
    password = hash_str(password)

    new_user = User(username=username.lower(), password=password, birthday=birthday)
    db.session.add(new_user)
    db.session.add(User_Settings(username=username))
    db.session.commit()
    return new_user

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

def remove_message(mess_id):
    """
    marks a message as removed in the database
    """
    the_message = Message.query.filter_by(id_=mess_id).first()
    if not the_message:
        raise RowDoesNotExist(f"message id {mess_id} does not exist")
    the_message.removed = 1
    db.session.add(the_message)
    db.session.commit()

def check_api_key(api_key):
    """
    Checks whether the api key given is valid
    """
    if Api_Key.query.filter_by(key=api_key).scalar():
        return True
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

def update_usersettings(username, hwm_notif=None, fm_notif=None, mess_notif=None):
    """
    updates the user settings,
    if no new settings were provided will not update,
    will return the usersettings obj

    args:
        username: the id of the users account
        hwm_notif, fm_notif, mess_notif: the new value
    """
    user_setting = User_Settings.query.filter_by(username=username).first()
    if not user_setting:
        raise RowDoesNotExist("User settings row does not exist")
    if hwm_notif:
        user_setting.hwm_notif = hwm_notif
    if fm_notif:
        user_setting.fm_notif = fm_notif
    if mess_notif:
        user_setting.mess_notif = mess_notif
    if hwm_notif and fm_notif and mess_notif:
        db.session.add(user_setting)
        db.session.commit()
    return user_setting

def get_notifations(username):
    """
    returns a generator of all notifications as Notification objects

    args:
        username : the username for getting different notifications
    """
    usr_setting = User_Settings.query.filter_by(username=username).first()
    if usr_setting.fm_notif == 1:
        fm_expiring = get_fm4_expiring(count=True)
        if fm_expiring > 0:
            yield Notification(f"You have {fm_expiring} expiring items in the freezer", "warning")
    if usr_setting.hwm_notif == 1:
        hw_due = Homework_Main.query.filter_by(removed=0).count()
        if hw_due > 0:
            yield Notification(f"You have {hw_due} outstanding homeworks", "warning")

def get_users(removed=0):
    """
    returns User obj's
    """
    return User.query.filter_by(removed=removed).all()
