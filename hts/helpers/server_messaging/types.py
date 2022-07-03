"""
enum types and server message dataclass for
sending server messages to the client using WebSocket
"""
from dataclasses import asdict, dataclass
from enum import IntEnum, unique

from simple_websocket import Server as WebSocket


@unique
class ConnType(IntEnum):
    """
    The format that the data will be
    sent/recieved through the WebSocket,
    decided upon connection by client
    """
    JSON = 1
    MSGPACK = 2


@unique
class MessageTypes(IntEnum):
    """
    The valid payload type int's
    that can be sent to the client
    (the message)
    """
    NOTIFICATION = 1
    DB_UPDATE = 2
    UPLOAD_PROGRESS = 3


@unique
class DBUpdateTypes(IntEnum):
    """
    database update types for inside the payload
    """
    ADD = 1
    MODIFY = 2
    DELETE = 3


@unique
class NotifTypes(IntEnum):
    """
    notification types for inside the payload
    """
    MESSAGE = 1


class Payload(dict):
    """
    Used to hold the WebSocket payload,
    it is a dict object with added classmethods
    that allow for easy and DRY creation of payloads
    """
    @classmethod
    def create_notification(cls, type_id: int, message, category="message"):
        """
        generates a notification payload

            :param type_id: the type of notification
            :param message: the message to send to the user
        """
        if type_id not in [item.value for item in NotifTypes]:
            raise ValueError("Unknown Notification type id")
        return cls(type_id=type_id, message=message, category=category)

    @classmethod
    def create_dbupdate(cls, type_id: int, where, row_id):
        """
        generates a database update payload

            :param type_id: the type of dbupdate
            :param where: what 'table' row was updated
            :param row_id: the id of the row
        """
        if type_id not in [item.value for item in DBUpdateTypes]:
            raise ValueError("Unknown DBUpdateType type id")
        return cls(type_id=type_id, where=where, row_id=row_id)

    @classmethod
    def create_progress(cls, context_id, perc: int):
        """
        generates a progress update payload,
        could be a file uploading to the server or processing

            :param context_id: the related progress element(given
                               from client on upload) id to update
            :param perc: the current percent from 0-100
        """
        if perc < 0 or perc > 100:
            raise ValueError("percent range is incorrect must be 0-100")
        return cls(context_id=context_id, perc=perc)


@dataclass
class ServerMessage:
    """
    A dataclass for the structure
    of WebSocket messages

        :param m_type: value from MessageTypes
        :param payload: the payload to send (dict)
    """
    m_type: int
    payload: Payload

    @property
    def asdict(self) -> dict:
        """
        uses the dataclasses.asdict
        method to convert the
        dataclass into a dict
        """
        return asdict(self)

    @classmethod
    def fromdict(cls, obj: dict):
        """
        converts a dict object into a ServerMessage

            :param obj: a dict object to convert
                        into a ServerMessage
        """
        return cls(obj["m_type"], obj["payload"])


@dataclass
class QueuedMessage:
    """
    Dataclass that contains needed data
    for when a WebSocket message is queued

        :param message: the ServerMessage that will
                        be sent through a WebSocket
        :param curr_client_id: the clients id, can be None
        :param curr_device_id: the device's id, can be None
        :param app_name: the name of the 'app' that the
                         message was sent from, can be None
    """
    message: ServerMessage
    curr_client_id: str | None = None
    curr_device_id: str | None = None
    app_name: str | None = None


@dataclass
class DeviceConnection:
    """
    used to store WebSocket connection data

        :param socket: the socket containing the connection
        :param transport_type: how the data will be packed in messages
        :param notify_apps: the apps the user wants to be notifed for
    """
    socket: WebSocket
    transport_type: ConnType = ConnType.JSON
    # TODO: change to set type later?
    notify_apps: tuple = ()
