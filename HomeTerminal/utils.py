"""
Small functions which do useful things
"""
import datetime
import hashlib
import os
from functools import lru_cache
from io import BytesIO

from flask import current_app
from PIL import Image


def is_allowed_img_file(filename):
    """
    Checks whether given filename has an allowed extention
    """
    return '.' in filename and \
        filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_IMG_EXT"]
        #TODO: remove the use of current app here

def compress_jpg_thumbnail(img_bytes, max_size, quality):
    """
    Will convert img given to jpeg and compress,
    returns the bytesio object

    args
        img_bytes : io.ByteIO
        max_size: the max size of the image e.g. (100, 100)
        quality: the quality used in the jpeg compression
    """
    raw_image = Image.open(img_bytes)
    converted_img = BytesIO()
    raw_image = raw_image.convert("RGB")
    raw_image.thumbnail(max_size)
    raw_image.save(converted_img, format="JPEG", quality=quality)
    converted_img.seek(0)
    return converted_img

def get_hash_image(img_bytes, ext=None, base_path=None):
    """
    returns the filename/path with the hash of the image

    args:
        img_bytes : the bytes to hash
        ext : the extention to give the filename (if provided)
        base_path : path to add before filename (if provided)
    """
    path = hashlib.sha256(img_bytes).hexdigest().__str__()
    if ext:
        path = path + ext
    if base_path:
        path = os.path.join(base_path, path)
    return path

@lru_cache(maxsize=15)
def calc_expire_date(months):
    """
    Returns date
    excepts months betweeen 0-12
    """
    try:
        months = int(months)
    except ValueError:
        months = 0

    if months == 0:
        days = 7
    elif months == 1:
        days = 30
    elif months == 2:
        days = 60
    elif months == 3:
        days = 91
    elif months == 4:
        days = 121
    elif months == 5:
        days = 152
    elif months == 6:
        days = 182
    elif months == 7:
        days = 212
    elif months == 8:
        days = 243
    elif months == 9:
        days = 273
    elif months == 10:
        days = 304
    elif months == 11:
        days = 334
    elif months == 12:
        days = 365
    else:
        return None
    return datetime.datetime.now() + datetime.timedelta(days=days)


class Notification:
    """
    used to store each notfication for the user
    """
    def __init__(self, content, category="message"):
        self.content = content
        self.category = category
