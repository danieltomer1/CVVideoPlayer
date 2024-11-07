from dataclasses import dataclass
from enum import Enum, auto
from typing import Tuple, Union

from pynput.mouse import Button

from .video_player_utils import SupportedOS
from .windows_vk_dict import VK_CODE_MAP

mouse_button_parser = {
    Button.left: "mouse_left",
    Button.right: "mouse_right",
    Button.middle: "mouse_middle",
}

MODIFIERS = {
    "ctrl",
    "alt",
    "shift",
}


def make_vk_code_mapper(os: SupportedOS):
    if os == SupportedOS.LINUX:
        return chr
    elif os == SupportedOS.WINDOWS:
        return lambda x: VK_CODE_MAP[x]
    else:
        raise NotImplementedError(f"{os=} not supported")


class Singleton(type):
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

