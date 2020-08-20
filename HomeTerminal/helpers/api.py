"""
decorator methods for use with the api routes
"""
from contextlib import wraps

from flask import abort, jsonify, request
from flask_login import current_user

from ..database.dao.exceptions import AlreadyUpToDate
from ..database.dao.user import check_api_key


def api_auth(fn):
    """
    decorator
    Used to make sure that the api key
    or user cookie is used to use api
    """
    @wraps(fn)
    def wrap(*args, **kwargs):
        if not current_user.is_anonymous:
            # allow cookie auth
            return fn(*args, **kwargs)
        elif check_api_key(request.headers.get("x-api-key", default="", type=str)):
            # allow api-key sent in request header
            return fn(*args, **kwargs)
        else:
            return abort(401)
    return wrap

def api_date_checks(fn):
    """
    decorator that returns json for the date
    """
    @wraps(fn)
    def wrap(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except AlreadyUpToDate:
            return jsonify({"error": "AlreadyUpToDate", "loaded_data":tuple()})
        except ValueError:
            return jsonify({"error":"datetime not in correct format of YYYY/MM/DD H:M:S.MS"})
    return wrap
