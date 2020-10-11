"""
constants for use inside the program
"""
from uuid import UUID

from .types import Widget
from .widgets import (generate_message_widget, generate_shortcut_widget,
                      generate_weather_widget)

# widgets that are inbuilt to the HTS
INBUILT_WIDGETS = (
        Widget(
            UUID(bytes=b"\x17\x08wX\xac\xc5Ca\x8f\x05bb<B\x93\xa9", version=4),
                "messages", generate_message_widget, None),
        Widget(
            UUID(bytes=b"\tmE\xdc\xdbCJ\xe4\x968\xa1\xf5C\x00\x9c\xc3", version=4),
                "shortcuts", generate_shortcut_widget, "shortcuts.index"),
        Widget(
            UUID(bytes=b"\xfe\xe6\xac\xac\xd3\xcaGq\x8a\xa5\x8dz;\xe0\x89Y", version=4),
                "weather", generate_weather_widget, None)
    )

# default widgets to give the user on account creation
DEFAULT_WIDGETS = (
    INBUILT_WIDGETS[0],
    INBUILT_WIDGETS[2]
)
