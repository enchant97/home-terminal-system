import logging
from datetime import datetime

from .models import User, User_Settings, db
from .utils import hash_str

class RowAlreadyExists(Exception):
    pass

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

def new_account(username, password, birthday: datetime):
    """
    creates a new account in the database
    """
    if User.query.filter_by(username=username).scalar():
        # if the username already exists
        raise RowAlreadyExists(f"username already exists: {username}")
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
