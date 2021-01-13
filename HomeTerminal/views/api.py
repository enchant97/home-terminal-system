from flask import Blueprint, jsonify, request

from ..database import dao
from ..helpers.api import api_auth

api = Blueprint("api", __name__)

@api.route("/is-healthy")
def is_healthy():
    """
    route for health check,
    when running in docker
    """
    return jsonify(status="OK")

@api.route("/im/get-names", methods=["POST"])
@api_auth
def get_im_getnames():
    name = request.json["itemname"]
    item_rows = dao.inventory_manager.get_like_item_names(name, 4)

    return jsonify({"item_names": [i.name for i in item_rows]})

@api.route("fm/get-expiring-count")
@api_auth
def get_fm_expiring():
    return jsonify(count=dao.freezer_manager.get_fm4_expiring(count=True))

@api.route("/reminder/tasks/<int:task_id>", methods=["DELETE"])
@api_auth
def delete_reminder_task(task_id):
    dao.reminder.remove_reminder_task(task_id)
    return jsonify(status="ok")
