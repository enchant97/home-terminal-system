import uuid

from flask import Blueprint, current_app
from flask_login import current_user, login_required
from flask_sock import Sock
from simple_websocket import Server as WebSocket
from simple_websocket import ConnectionError, ConnectionClosed

from ..helpers.checkers import json_dict
from ..helpers.server_messaging.types import DeviceConnection
from ..sockets import message_handler

sock = Sock()


@sock.route("/live-update/listen")
@login_required
def listen(socket: WebSocket):
    user_id = current_user.id_
    device_id = uuid.uuid4().hex
    try:

        while True:
            message = socket.receive()
            json_msg = json_dict(message)
            if json_msg.get("transport_type"):
                # TODO: handle unknown transport types
                device_conn = DeviceConnection(
                    socket, json_msg["transport_type"],
                    tuple(json_msg["notify_apps"]))
                message_handler.new_client(user_id, device_id, device_conn)

    except ConnectionClosed:
        current_app.logger.debug(
            "client's WebSocket lost connection with server, {user_id} {device_id}")

    finally:
        message_handler.remove_client(user_id, device_id)
