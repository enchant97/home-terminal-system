from datetime import datetime

from ...utils import Notification
from ..database import db
from ..models.homework import Main as Homework_Main
from ..models.user import Api_Key, Message, User, User_Settings
from .exceptions import AlreadyUpToDate, RowAlreadyExists, RowDoesNotExist
from .freezer_manager import get_fm4_expiring


def try_login_user(username, password):
    """
    returns user obj and sets last login date, if password and username match
    """
    the_user = User.query.filter_by(username=username).first()
    if the_user:
        if the_user.check_password(password):
            the_user.lastlogin = datetime.utcnow()
            db.session.add(the_user)
            db.session.commit()
            return the_user
    return None

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

    new_user = User(username=username.lower(), birthday=birthday)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    db.session.add(User_Settings(user_id=new_user.id_))
    db.session.commit()
    return new_user

def change_user_password(username, new_password, old_password):
    """
    returns user obj if password change was success
    """
    the_user = User.query.filter_by(username=username).first()
    if the_user:
        if the_user.check_password(old_password):
            the_user.set_password(new_password)
            db.session.add(the_user)
            db.session.commit()
            return the_user
    return None

def new_message(user_from, message):
    """
    adds a new message into database,
    returns message obj on success

    args:
        user_from : the username that the message is from
        message : the message
    """
    the_user = User.query.filter_by(username=user_from).first()
    if not the_user:
        raise RowDoesNotExist(f"username {user_from} not found")
    the_message = Message(user_id_from=the_user.id_, message=message)
    db.session.add(the_message)
    db.session.commit()
    return the_message

def remove_message(mess_id, removed=True):
    """
    marks a message as removed in the database

    args:
        mess_id : the id of the message to mark removed
        removed : allows for entry to be unmarked for removal
    """
    the_message = Message.query.filter_by(id_=mess_id).first()
    if not the_message:
        raise RowDoesNotExist(f"message id {mess_id} does not exist")
    the_message.removed = removed
    db.session.add(the_message)
    db.session.commit()

def check_api_key(api_key):
    """
    Checks whether the api key given is valid

    args:
        api_key : the api key to check
    """
    if Api_Key.query.filter_by(key=api_key).scalar():
        return True
    return False

def get_messages(removed=False, last_updated=None):
    """
    Returns the messages,
    if last_updated is datetime will raise
    AlreadyUpToDate if it is already up to date

    args:
        removed : whether to select removed entries or not
        last_updated : datetime obj or '%Y-%m-%d %H:%M:%S.%f' (expects UTC)
    """
    if last_updated:
        if not isinstance(datetime, last_updated):
            # if the last_updated was a string try to convert
            last_updated = datetime.strptime(last_updated, "%Y-%m-%d %H:%M:%S.%f")
        last_message = Message.query.filter_by(removed=removed).order_by(Message.last_updated.desc()).first()
        if last_message:
            if last_message.last_updated <= last_updated:
                raise AlreadyUpToDate()

    return Message.query.filter_by(removed=removed).all()

def update_usersettings(username, hwm_notif=None, fm_notif=None, mess_notif=None):
    """
    updates the user settings,
    if no new settings were provided will not update,
    will return the usersettings obj

    args:
        username: the id of the users account
        hwm_notif, fm_notif, mess_notif: the new value (BOOL)
    """
    the_user = User.query.filter_by(username=username).first()
    if the_user:
        user_setting = User_Settings.query.filter_by(username=the_user.id_).first()
        if not user_setting:
            raise RowDoesNotExist("User settings row does not exist")
        if hwm_notif is not None:
            user_setting.hwm_notif = hwm_notif
        if fm_notif is not None:
            user_setting.fm_notif = fm_notif
        if mess_notif is not None:
            user_setting.mess_notif = mess_notif
        db.session.add(user_setting)
        db.session.commit()
        return user_setting
    raise RowDoesNotExist(f"username {username} does not exist")

def get_notifations(username):
    """
    returns a generator of all notifications as Notification objects

    args:
        username : the username for getting different notifications
    """
    the_user = User.query.filter_by(username=username).first()
    if the_user:
        usr_setting = User_Settings.query.filter_by(username=the_user.id_).first()
        if usr_setting.fm_notif is True:
            fm_expiring = get_fm4_expiring(count=True)
            if fm_expiring > 0:
                yield Notification(
                    f"You have {fm_expiring} expiring items in the freezer",
                    "warning")
        if usr_setting.hwm_notif is True:
            hw_due = Homework_Main.query.filter_by(removed=False).count()
            if hw_due > 0:
                yield Notification(f"You have {hw_due} outstanding homeworks", "warning")
    raise RowDoesNotExist(f"username {username} does not exist")

def get_users(removed=False):
    """
    returns User obj's
    """
    return User.query.filter_by(removed=removed).all()
