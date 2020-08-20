import uuid

from flask import Blueprint, current_app
from flask_login import current_user, login_required
from geventwebsocket.exceptions import WebSocketError
from geventwebsocket.websocket import MSG_SOCKET_DEAD, WebSocket

from ..helpers.checkers import json_dict
from ..helpers.server_messaging.types import DeviceConnection
from ..sockets import message_handler

live_update_ws = Blueprint(__name__, "liveupdate-ws")

@live_update_ws.route("/listen")
@login_required
def listen(socket: WebSocket):
    try:
        user_id = current_user.id_
        device_id = uuid.uuid4().hex

        while not socket.closed:
            message = socket.receive()
            json_msg = json_dict(message)
            if json_msg.get("transport_type"):
                #TODO: handle unknown transport types
                device_conn = DeviceConnection(
                    socket, json_msg["transport_type"],
                    tuple(json_msg["notify_apps"]))
                message_handler.new_client(user_id, device_id, device_conn)

    except WebSocketError as err:
        if err.args[0] == MSG_SOCKET_DEAD:
            current_app.logger.debug(
                f"client's WebSocket lost connection with server, {user_id} {device_id}")
        else:
            raise err

    message_handler.remove_client(user_id, device_id)
