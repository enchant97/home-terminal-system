from functools import lru_cache
from pathlib import Path
from typing import Tuple

from pydantic import BaseSettings


class Settings(BaseSettings):
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    DEBUG: bool = False
    TESTING: bool = False

    MAX_IMAGE_SIZE: Tuple[int, int] = (800, 800)
    JPEG_QUALITY: int = 65
    ALLOWED_IMG_EXT: tuple = ("jpg", "jpeg", "png", "bmp")
    ADMIN_USERNAME: str = "terminal"
    IMG_PATH: Path = None
    ENABLE_PLUGINS: bool = True
    MAX_SOCKET_MESS: int = 100
    MAX_SOCKET_PUT_WAIT: int = 4

    SECRET_KEY: str
    DATABASE_URI: str

    class Config:
        case_sensitive = True
        env_file = '.env'


@lru_cache()
def get_settings():
    """
    returns the Settings obj
    """
    return Settings()
