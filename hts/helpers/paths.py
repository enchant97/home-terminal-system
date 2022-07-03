"""
helper functions that will be useful with handling paths in the app
"""

from pathlib import Path

from flask import current_app


def get_image_folder(dynamic_img_name: str) -> Path:
    """
    used to get the dynamic image path for
    a certain app/plugin from the config

        :param dynamic_img_name: the key of the dynamic image path
        :return: the folder path
        :rtype: pathlib.Path
    """
    base_path = Path(current_app.config["BASE_IMG_PATH"])
    dynamic_img_path = current_app.config["DYNAMIC_IMG_LOCATIONS"] \
        .get(dynamic_img_name, dynamic_img_name.lower())
    image_path = Path(dynamic_img_path)
    if not image_path.is_absolute():
        # if path is relative join the base_path onto it
        image_path = base_path.joinpath(image_path)
    # make sure folder are created
    image_path.mkdir(exist_ok=True, parents=True)
    return image_path


def is_allowed_img_file(filename: str) -> bool:
    """
    Checks whether given filename has an allowed extention

        :param filename: the filename of the file
        :return: whether the filename is allowed
        :rtype: True, False
    """
    return Path(filename).suffix.removeprefix(".") in current_app.config["ALLOWED_IMG_EXT"]
