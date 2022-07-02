"""
helpers to handle photo convertion
"""

import hashlib
from io import BytesIO

from PIL import Image


def compress_jpg_thumbnail(img_bytes, max_size, quality) -> BytesIO:
    """
    Will convert img given to jpeg and compress

        :param img_bytes: io.ByteIO
        :param max_size: the max size of the image e.g. (100, 100)
        :param quality: the quality used in the jpeg compression
        :return: the compressed image ready for writing
        :rtype: io.BytesIO
    """
    raw_image = Image.open(img_bytes)
    converted_img = BytesIO()
    raw_image = raw_image.convert("RGB")
    exif = raw_image.info.get("exif")
    raw_image.thumbnail(max_size)
    if exif:
        raw_image.save(converted_img, format="JPEG",
                       quality=quality, exif=exif)
    else:
        raw_image.save(converted_img, format="JPEG", quality=quality)
    converted_img.seek(0)
    return converted_img


def get_hash_image(img_bytes, ext="") -> str:
    """
    returns the filename as the hash of the image

        :param img_bytes: the bytes to hash
        :param ext: the extention to give the filename e.g .jpg
        :return: filename
        :rtype: str
    """
    return hashlib.sha256(img_bytes).hexdigest() + ext
