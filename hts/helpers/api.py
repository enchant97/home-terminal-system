"""
decorator methods for use with the api routes
"""
from functools import wraps
from uuid import UUID

from flask import jsonify, request
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

        api_key = request.headers.get("x-api-key", default=None, type=str)
        if api_key:
            try:
                if check_api_key(UUID(api_key, version=4)):
                    # allow api-key sent in request header
                    return fn(*args, **kwargs)
                # api key was invalid
                return jsonify(status="invalid x-api-key"), 401
            except ValueError as err:
                # invalid format for api key
                return jsonify(status=err.args[0]), 401
        # no api key or cookie given in request
        return jsonify(status="No x-api-key header or session cookie"), 401
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
            return jsonify({"error": "AlreadyUpToDate", "loaded_data": tuple()})
        except ValueError:
            return jsonify({"error": "datetime not in correct format of YYYY/MM/DD H:M:S.MS"})
    return wrap
