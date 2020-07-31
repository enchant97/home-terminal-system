"""
functions for checking stuff
"""
from flask import current_app


def is_admin(username):
    """
    checks whether the user is a admin

        :param username: username to check against
        :return: whether the user is a admin
        :rtype: True/False
    """
    if username == current_app.config.get("ADMINUSERNAME"):
        return True
    return False
