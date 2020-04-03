"""
Stores the apps configs
"""

config = {
    "dev": "HomeTerminal.config.Development",
    "prod": "HomeTerminal.config.Production",
    "test": "HomeTerminal.config.Testing"
}

class Base:
    DEBUG = False
    TESTING = False
    SERVER_ERROR_MESSAGE = "SERVER ERROR! Try again later with your request"
    ADMINUSERNAME = "terminal"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "abf5f6a68b734dc38332278c83ae8bb1"
    SQLALCHEMY_DATABASE_URI = "sqlite://:memory:"
    MAX_IMAGE_SIZE = (800, 800)
    JPEG_QUALITY = 65
    ALLOWED_IMG_EXT = ("jpg", "jpeg", "png", "bmp")
    # folder to store folders with uploaded pictures, set to None to stop saving
    IMG_LOCATION = None

class Testing(Base):
    """
    Used for testing with pytest

    """
    ENV = "test"
    TESTING = True

class Development(Base):
    """
    The development config
    """
    ENV = "dev"
    DEBUG = True

class Production(Base):
    ENV = "prod"
