from flask import Blueprint, jsonify, request

from ..database import dao
from ..helpers.api import api_auth

api = Blueprint("api", __name__)

@api.route("/im/get-names", methods=["POST"])
@api_auth
def get_im_getnames():
    name = request.json["itemname"]
    item_rows = dao.inventory_manager.get_like_item_names(name, 4)

    return jsonify({"item_names": [i.name for i in item_rows]})
