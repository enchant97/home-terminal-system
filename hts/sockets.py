"""
contains the socket handler
"""
from flask import Flask

from .helpers.server_messaging.socket_handler import MessageSocketsHandler

message_handler = MessageSocketsHandler()


def init_socket_handlers(app: Flask):
    message_handler.max_queued_messages = app.config.get(
        "MAX_SOCKET_MESS", 100)
    message_handler.put_timout = app.config.get("MAX_SOCKET_PUT_WAIT", 4)
    message_handler.start()
