"""
contains the main class for handling sending messages to connected clients
"""
from collections import defaultdict
from json import dumps
from queue import Queue
from threading import Thread

from geventwebsocket.websocket import WebSocket
from msgpack import packb

from ...helpers.server_messaging.types import (ConnType, DeviceConnection,
                                               QueuedMessage, ServerMessage)


def pack_and_send(socket: WebSocket, msg: DeviceConnection, transport_type: ConnType):
    """
    packs and sends the message over a WebSocket
    """
    #TODO make this just a multi packer
    if transport_type == ConnType.JSON:
        socket.send(dumps(msg.asdict))
    elif transport_type == ConnType.MSGPACK:
        socket.send(packb(msg.asdict))
    else:
        raise ValueError(f"Unknown transport type {transport_type}")

class MessageSocketsHandler(Thread):
    """
    Handles the queued messages for sending from a seperate thread

        :param max_messages: max queued messages for
                                each connection, if maxsize
                                is <= 0 size is 'infinite'
        :param wait_timeout: timeout for put method in each queue
    """
    def __init__(self, max_messages: int = 100, wait_timeout: int = None):
        super().__init__(daemon=True, name="MessageSocketThread")
        self.__connected_clients = defaultdict(dict)
        self.__queued_messages = Queue(max_messages)
        self.__wait_timeout = wait_timeout

    @property
    def connected_clients(self):
        return self.__connected_clients

    @property
    def max_queued_messages(self):
        return self.__queued_messages.maxsize

    @max_queued_messages.setter
    def max_queued_messages(self, new_max):
        self.__queued_messages.maxsize = int(new_max)

    @property
    def put_timout(self):
        return self.__wait_timeout

    @put_timout.setter
    def put_timout(self, new_timeout):
        self.__wait_timeout = int(new_timeout)

    def send_message(self, message: ServerMessage, client_id=None, device_id=None):
        """
        allows the sending of a socket message to a client,
        puts it into the message queue

            :param message: the ServerMessage to send through a socket
            :param client_id: the clients current user id
            :param device_id: the clients current current device id
        """
        if client_id is None or self.__connected_clients.get(client_id):
            mess_to_queue = QueuedMessage(message, client_id, device_id)
            self.__queued_messages.put(mess_to_queue, timeout=self.__wait_timeout)

    def new_client(self, client_id, device_id, device_conn: DeviceConnection):
        """
        allows for adding a new client socket.

            :param client_id: the clients user id
            :param device_id: the clients device id
            :param device_conn: the device connection to add
        """
        self.__connected_clients[client_id][device_id] = device_conn

    def remove_client(self, client_id, device_id):
        """
        allows for removing a client,
        does not close the socket connections

            :param client_id: the clients user id
            :param device_id: the clients device id
        """
        del self.__connected_clients[client_id][device_id]
        if not self.__connected_clients[client_id]:
            del self.__connected_clients[client_id]

    def run(self):
        """
        starts the thread loop
        """
        #TODO: pack both types before and send later to all clients!
        while True:
            next_message: QueuedMessage = self.__queued_messages.get()

            if next_message.curr_client_id is None:
                # sending to all connected users/devices
                for user_id in self.__connected_clients:
                    for device_id in self.__connected_clients[user_id]:
                        pack_and_send(
                            self.__connected_clients[user_id][device_id].socket,
                            next_message.message,
                            self.__connected_clients[user_id][device_id].transport_type
                            )
            else:
                # send to a specific user
                user_id = next_message.curr_client_id
                client_sockets: dict = self.__connected_clients[user_id]
                for device_id in client_sockets:
                    if device_id != next_message.curr_device_id:
                        pack_and_send(
                            self.__connected_clients[user_id][device_id].socket,
                            next_message.message,
                            self.__connected_clients[user_id][device_id].transport_type
                            )
            self.__queued_messages.task_done()
