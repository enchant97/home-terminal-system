"""
Stores the apps configs
"""

config = {
    "dev": "HomeTerminal.config.Development",
    "prod": "HomeTerminal.config.Production"
}

class Base:
    DEBUG = False
    TESTING = False
    SERVER_ERROR_MESSAGE = "SERVER ERROR! Try again later with your request"
    ADMINUSERNAME = "terminal"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "abf5f6a68b734dc38332278c83ae8bb1"
    SQLALCHEMY_DATABASE_URI = "sqlite://"

class Development(Base):
    """
    The development config
    """
    ENV = "dev"
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

class Production(Base):
    ENV = "prod"
