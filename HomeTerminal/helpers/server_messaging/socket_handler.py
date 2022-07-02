"""
contains the main class for handling sending messages to connected clients
"""
from collections import defaultdict
from json import dumps
from queue import Queue
from threading import Thread

from msgpack import packb
from simple_websocket import ConnectionClosed

from ...helpers.server_messaging.types import (ConnType, DeviceConnection,
                                               QueuedMessage, ServerMessage)


def pack(msg: ServerMessage):
    """
    packs message as json and msgpack

        :param msg: the ServerMessage obj to send
        :return: json.dumps and msgpack.packb
    """
    msg_dict = msg.asdict
    return dumps(msg_dict), packb(msg_dict)


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

    def send_message(self, message: ServerMessage, client_id=None, device_id=None, app_name=None):
        """
        allows the sending of a socket message to a client,
        puts it into the message queue

            :param message: the ServerMessage to send through a socket
            :param client_id: the clients current user id
            :param device_id: the clients current current device id
            :param app_name: the name of the 'app' that the message was sent from
        """
        if client_id is None or self.__connected_clients.get(client_id):
            mess_to_queue = QueuedMessage(
                message, client_id, device_id, app_name)
            self.__queued_messages.put(
                mess_to_queue, timeout=self.__wait_timeout)

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
        if self.__connected_clients[client_id].get(device_id):
            del self.__connected_clients[client_id][device_id]
        if not self.__connected_clients[client_id]:
            del self.__connected_clients[client_id]

    def run(self):
        """
        starts the thread loop
        """
        # TODO: refactor later
        clients_to_remove = []
        while True:
            next_message: QueuedMessage = self.__queued_messages.get()
            print(len(self.__connected_clients))
            # (JSON, MSGPACK)
            packed_msg = pack(next_message.message)
            if next_message.curr_client_id is None:
                # sending to all connected users/devices
                for user_id in self.__connected_clients:
                    for device_id in self.__connected_clients[user_id]:
                        try:
                            curr_client = self.__connected_clients[user_id][device_id]
                            # only send the message if the client is listening for the current app
                            if (next_message.app_name is None) or (next_message.app_name in curr_client.notify_apps):
                                if curr_client.transport_type == ConnType.MSGPACK:
                                    curr_client.socket.send(packed_msg[1])
                                else:
                                    curr_client.socket.send(packed_msg[0])
                        except ConnectionClosed:
                            clients_to_remove.append((user_id, device_id))
                        except KeyError:
                            pass
            else:
                # send to a specific user
                user_id = next_message.curr_client_id
                client_sockets: dict = self.__connected_clients[user_id]
                for device_id in client_sockets:
                    if device_id != next_message.curr_device_id:
                        try:
                           curr_client = self.__connected_clients[user_id][device_id]
                           # only send the message if the client is listening for the current app
                           if (next_message.app_name is None) or (next_message.app_name in curr_client.notify_apps):
                               if curr_client.transport_type == ConnType.MSGPACK:
                                   curr_client.socket.send(packed_msg[1])
                               else:
                                   curr_client.socket.send(packed_msg[0])
                        except ConnectionClosed:
                            clients_to_remove.append((user_id, device_id))
                        except KeyError:
                            pass

            self.__queued_messages.task_done()

            for client_id, device_id in clients_to_remove:
                self.remove_client(user_id, device_id)
