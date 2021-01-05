import hashlib
import uuid
from datetime import datetime

from ...helpers.constants import DEFAULT_WIDGETS
from ...helpers.types import Notification
from ..database import db
from ..models.user import Api_Key, Message, User, User_Settings
from .dashboard import add_widget
from .exceptions import AlreadyUpToDate, RowAlreadyExists, RowDoesNotExist
from .freezer_manager import get_fm4_expiring
from .reminder import get_reminders_due


def try_login_user(username: str, password: str) -> User:
    """
    returns user obj and sets last login date,
    if password and username match

        :param username: the username to check against
        :param password: the password to check against
        :return: the User obj or None
    """
    the_user = User.query.filter_by(username=username).first()
    if the_user:
        if the_user.check_password(password):
            the_user.lastlogin = datetime.utcnow()
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

    # create the user row
    new_user = User(username=username.lower(), birthday=birthday)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    # create the user setting row
    db.session.add(User_Settings(user_id=new_user.id_))

    # create the user widget rows
    for i, widget in enumerate(DEFAULT_WIDGETS):
        add_widget(new_user.id_, widget.uuid)
    db.session.commit()
    return new_user

def change_user_password(user_id: int, new_password: str, old_password: str) -> User:
    """
    used to change a users password

        :param user_id: the users id column
        :param new_password: the new password
        :param old_password: the old password
        :return: the user row or None if none exists
    """
    the_user = User.query.filter_by(id_=user_id).first()
    if the_user:
        if the_user.check_password(old_password):
            the_user.set_password(new_password)
            db.session.commit()
            return the_user
    return None

def new_message(user_from_id: int, message: str) -> Message:
    """
    adds a new message into database,
    returns message obj on success

        :param user_from_id: the user id that the message is from
        :param message: the message
        :raises: RowDoesNotExist if user row is not found
        :return: the created message
    """
    if User.query.filter_by(id_=user_from_id).scalar() is None:
        raise RowDoesNotExist(f"the user with id {user_from_id} not found")
    the_message = Message(user_id_from=user_from_id, message=message)
    db.session.add(the_message)
    db.session.commit()
    return the_message

def remove_message(mess_id, removed=True):
    """
    marks a message as removed in the database

        :param mess_id: the id of the message to mark removed
        :param removed: allows for entry to be unmarked for removal
    """
    the_message = Message.query.filter_by(id_=mess_id).first()
    if not the_message:
        raise RowDoesNotExist(f"message id {mess_id} does not exist")
    the_message.removed = removed
    db.session.add(the_message)
    db.session.commit()

def check_api_key(api_key) -> bool:
    """
    Checks whether the api key given is valid

        :param api_key: the api key to check
        :return: whether api key is valid
    """
    if Api_Key.query.filter_by(key=api_key).scalar() is None:
        return False
    return True

def get_api_key(user_id: int) -> Api_Key:
    """
    returns a api key given to the given username,
    will create one if none is found for that user

        :param user_id: the id of a user in the users table
        :raises RowDoesNotExist: if user with id is not found
        :return: the API key
    """
    if User.query.filter_by(id_=user_id, removed=False).scalar() is None:
        raise RowDoesNotExist(f"user with id: {user_id} not found")

    the_key = Api_Key.query.filter_by(owner_id=user_id).first()
    if not the_key:
        # make the api key if it does not exist
        key = str(hashlib.sha512(str(uuid.uuid4()).encode()).hexdigest())
        the_key = Api_Key(key=key, owner_id=user_id)
        db.session.add(the_key)
        db.session.commit()
    return the_key

def get_messages(removed=False, last_updated=None):
    """
    Returns the messages,
    if last_updated is datetime will raise
    AlreadyUpToDate if it is already up to date

        :param removed: whether to select removed entries or not
        :param last_updated: datetime obj or '%Y-%m-%d %H:%M:%S.%f' (expects UTC)
    """
    if last_updated:
        if not isinstance(datetime, last_updated):
            # if the last_updated was a string try to convert
            last_updated = datetime.strptime(last_updated, "%Y-%m-%d %H:%M:%S.%f")
        last_message = Message.query.filter_by(removed=removed)\
            .order_by(Message.last_updated.desc()).first()
        if last_message:
            if last_message.last_updated <= last_updated:
                raise AlreadyUpToDate()

    return Message.query.filter_by(removed=removed).all()

def update_usersettings(user_id: int, rem_notif=None, fm_notif=None, mess_notif=None):
    """
    updates the user settings,
    if no new settings were provided will not update,
    will return the usersettings obj

        :param user_id: the id of the users account
        :param rem_notif: the new value (BOOL)
        :param fm_notif: the new value (BOOL)
        :param mess_notif: the new value (BOOL)
        :raises RowDoesNotExist: if the user or user
                                 settings row is not found
        :return: the User_Settings obj
    """
    if User.query.filter_by(id_=user_id).scalar() is None:
        raise RowDoesNotExist(f"user with id {user_id} does not exist")

    user_setting = User_Settings.query.filter_by(user_id=user_id).first()
    if not user_setting:
        raise RowDoesNotExist("User settings row does not exist")
    if rem_notif is not None:
        user_setting.rem_notif = rem_notif
    if fm_notif is not None:
        user_setting.fm_notif = fm_notif
    if mess_notif is not None:
        user_setting.mess_notif = mess_notif
    db.session.commit()
    return user_setting

def get_notifations(user_id):
    """
    returns a generator of all notifications as Notification objects

        :param user_id: the user id to generate notifications for
    """
    usr_setting = User_Settings.query.filter_by(user_id=user_id).first()
    if usr_setting:
        if usr_setting.fm_notif is True:
            fm_expiring = get_fm4_expiring(count=True)
            if fm_expiring > 0:
                yield Notification(
                    f"You have {fm_expiring} expiring items in the freezer",
                    "warning")
        if usr_setting.rem_notif is True:
            reminders_due = get_reminders_due(user_id, True, True)
            if reminders_due > 0:
                yield Notification(f"You have {reminders_due} outstanding reminders", "warning")
    else:
        raise RowDoesNotExist(f"no settings row exists for user id: {user_id}")

def get_users(removed=False):
    """
    returns User obj's
    """
    return User.query.filter_by(removed=removed).all()

def delete_removed():
    """
    delete the rows that are marked as removed
    """
    User_Settings.query.filter_by(removed=True).delete()
    Api_Key.query.filter_by(removed=True).delete()
    Message.query.filter_by(removed=True).delete()
    User.query.filter_by(removed=True).delete()
    db.session.commit()
