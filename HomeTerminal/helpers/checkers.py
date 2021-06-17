"""
functions for checking stuff
"""
from json import JSONDecodeError, loads

from flask import current_app


def is_admin(username):
    """
    checks whether the user is a admin

        :param username: username to check against
        :return: whether the user is a admin
        :rtype: True/False
    """
    if username == current_app.config["ADMIN_USERNAME"]:
        return True
    return False


def json_dict(possible_json: str):
    """
    converts string to JSON, returns
    {} if it is not JSON

        :param possible_json: the str to check against
        :return: returns a dict of the JSON
                 or {} if its not JSON
    """
    try:
        return loads(possible_json)
    except (TypeError, JSONDecodeError):
        return {}
