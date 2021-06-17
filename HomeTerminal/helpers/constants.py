"""
constants for use inside the program
"""
from uuid import UUID

from .types import Widget
from .widgets import (generate_message_widget, generate_shortcut_widget,
                      generate_weather_widget)

# the folder names for dynamic images folder
INBUILT_DYNAMIC_IMG_FOLDERS = {
    "PHOTO_MANAGER": "photo_manager"
}

# widgets that are inbuilt to the HTS
INBUILT_WIDGETS = (
    Widget(
        UUID("17087758-acc5-4361-8f05-62623c4293a9"),
        "messages", generate_message_widget, None),
    Widget(
        UUID("096d45dc-db43-4ae4-9638-a1f543009cc3"),
        "shortcuts", generate_shortcut_widget, "shortcuts.index"),
    Widget(
        UUID("fee6acac-d3ca-4771-8aa5-8d7a3be08959"),
        "weather", generate_weather_widget, None)
)

# default widgets to give the user on account creation
DEFAULT_WIDGETS = (
    INBUILT_WIDGETS[0],
    INBUILT_WIDGETS[2]
)
