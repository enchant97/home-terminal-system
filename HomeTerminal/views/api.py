from flask import Blueprint, jsonify, request

from ..database import dao
from ..helpers.api import api_auth, api_date_checks

api = Blueprint("api", __name__)

@api.route("/hwm/hw")
@api_auth
@api_date_checks
def hw():
    loaded_hw = dao.homework.get_homework_ordered(last_updated=request.args.get("last-update"))
    return jsonify(loaded_data=[hw.serialize() for hw in loaded_hw])

@api.route("/im/get-names", methods=["POST"])
@api_auth
def get_im_getnames():
    name = request.json["itemname"]
    item_rows = dao.inventory_manager.get_like_item_names(name, 4)

    return jsonify({"item_names": [i.name for i in item_rows]})
