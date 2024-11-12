import abc
from dataclasses import dataclass
from enum import Enum, auto
from typing import Tuple, Union

from pynput import mouse


mouse_button_parser = {
    mouse.Button.left: "mouse_left",
    mouse.Button.right: "mouse_right",
    mouse.Button.middle: "mouse_middle",
}

MODIFIERS = {
    "ctrl",
    "alt",
    "shift",
}


class Singleton(abc.ABCMeta):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class InputType(Enum):
    KeyPress = auto()
    KeyRelease = auto()
    MouseScroll = auto()
    MouseClick = auto()
    MouseRelease = auto()
    MouseMove = auto()


@dataclass
class SingleInput:
    input_type: InputType
    input_data: Union[Tuple, str]
