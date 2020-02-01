import logging
from json import load
from uuid import uuid4

# what the config will use if a file is not found
CONFIG_DEFAULTS = {
    "db_path": "sqlite:///database.db",
    "secret_key": "replace me with a better key!",
    "server-error-message": "SERVER ERROR! Try again later with your request",
    "admin-username": "terminal"
}

class Config:
    """
    Allows for program to get config data from json file
    for different things for example database location
    """
    JSON_DATA = {}

    def __init__(self, filename):
        """Reads json data from required given filename"""
        self.__read(filename)

    def __read(self, filename):
        try:
            with open(filename, "r") as fo:
                self.JSON_DATA = load(fo)
        except FileNotFoundError:
            logging.exception("config file not found, will use defaults!")
            self.JSON_DATA = CONFIG_DEFAULTS

    def get_db_path(self):
        return self.JSON_DATA.get("db_path", "sqlite:///database.db")

    def get_secretkey(self):
        return self.JSON_DATA.get("secret_key", uuid4().hex)

    def get_schema_path(self):
        return self.JSON_DATA.get("schema_path", None)

    def get_server_error_message(self):
        return self.JSON_DATA.get("server-error-message", "error")

    def get_admin_username(self):
        return self.JSON_DATA.get("admin-username", "terminal")
