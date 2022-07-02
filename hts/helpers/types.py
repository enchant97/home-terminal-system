"""
Custom made types
"""
from dataclasses import dataclass
from types import FunctionType
from uuid import UUID

import msgpack
from sqlalchemy.types import LargeBinary, TypeDecorator


class Notification:
    """
    used to store each notfication for the user
    """

    def __init__(self, content, category="message"):
        self.content = content
        self.category = category


class BinaryMsgPack(TypeDecorator):
    """
    LargeBinary in database, allowing for the use of msgpack
    and without the need to msgpack.loads and msgpack.dumps
    """
    impl = LargeBinary

    def process_bind_param(self, value, dialect):
        if value:
            value = msgpack.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value:
            value = msgpack.loads(value)
        return value


class BinaryUUID4(TypeDecorator):
    """
    LargeBinary in database, allowing for the use of the uuid.UUID class
    """
    impl = LargeBinary

    def process_bind_param(self, value: UUID, dialect):
        if not isinstance(value, UUID):
            raise ValueError("value is not instance of uuid.UUID")
        if value:
            value = value.bytes
        return value

    def process_result_value(self, value, dialect):
        if value:
            value = UUID(bytes=value, version=4)
        return value


@dataclass
class Widget:
    """
    stores data about the widget

        :param uuid: the UUID4 of the widget
        :param name: the name of the widget
        :param generation_func: function to call when generating widget
        :param settings_endpoint: the endpoint to navigate to for configuring the widget
    """
    uuid: UUID
    name: str
    generation_func: FunctionType
    settings_endpoint: str

    @property
    def as_tuple(self):
        return self.uuid, self.name, self.generation_func, self.settings_endpoint
