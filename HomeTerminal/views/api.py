from contextlib import wraps
from datetime import datetime

from flask import Blueprint, abort, jsonify, request
from flask_login import current_user

from ..dao import check_api_key, get_homework_ordered, get_messages

api = Blueprint("api", __name__)

def api_auth(fn):
    """
    decorator
    Used to make sure that the api key
    or user cookie is used to use api
    """
    @wraps(fn)
    def wrap(*args, **kwargs):
        if current_user._id:
            # allow cookie auth
            return fn(*args, **kwargs)
        elif check_api_key(request.headers.get("x-api-key", default="", type=str)):
            # allow api-key sent in request header
            return fn(*args, **kwargs)
        else:
            return abort(401)

@api.route("/hwm/hw")
@api_auth
def hw():
    #TODO: seperate into DAO
    last_update = request.args.get("last_update", None)
    if last_update:
        try:
            last_update = datetime.strptime(last_update, "%Y-%m-%d %H:%M:%S.%f")
        except:
            return jsonify({"error":"datetime not in correct format of YYYY/MM/DD H:M:S.MS"})
        #TODO: find better way to do this (with database)
        # if LAST_HOMEWORK_UPDATE.is_uptodate(last_update):
        #     # if the client already is up-to date
        #     return jsonify({"error": "you already have the latest data", "loaded_data":tuple()})
    return jsonify(loaded_data=[hw.serialize() for hw in get_homework_ordered()])

@api.route("/messages")
@api_auth
def messages():
    return jsonify(messages=[message.serialize() for message in get_messages()])
