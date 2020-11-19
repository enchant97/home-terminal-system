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
    ADMINUSERNAME = "terminal"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "abf5f6a68b734dc38332278c83ae8bb1"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    MAX_IMAGE_SIZE = (800, 800)
    JPEG_QUALITY = 65
    ALLOWED_IMG_EXT = ("jpg", "jpeg", "png", "bmp")
    # the base path that all relative paths will use
    # controls where the app's dynamic images will be stored
    BASE_IMG_PATH = "dynamic_images"


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
    SQLALCHEMY_DATABASE_URI = "sqlite:///appdata.db"
