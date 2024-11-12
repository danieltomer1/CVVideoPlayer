import abc
from collections import defaultdict
from typing import Dict, Union
from queue import Queue

import cv2
from pynput import keyboard, mouse
from pynput.mouse import Button

from .utils.ui_utils import (
    mouse_button_parser,
    Singleton,
    SingleInput,
    InputType,
    MODIFIERS,
)

from .utils.video_player_utils import KeyFunction
from .utils.windows_os_utils import VK_CODE_MAP


class BaseInputParser(metaclass=Singleton):
    def __init__(self, allow_queue_buildup=False):
        self._allow_queue_buildup = allow_queue_buildup
        self._ui_queue: Queue[SingleInput] = Queue()
        self._modifiers = set()
        self._listeners = []

    def has_input(self) -> bool:
        return not self._ui_queue.empty()

    def get_input(self) -> SingleInput:
        return self._ui_queue.get(timeout=0.1)

    def start(self) -> None:
        self._listeners.append(
            keyboard.Listener(
                on_press=self._add_key_press_to_queue,
                on_release=self._add_key_release_to_queue,
            )
        )
        self._listeners.append(
            mouse.Listener(
                on_click=self._add_mouse_click_to_queue,
                on_scroll=self._add_mouse_scroll_to_queue,
            )
        )

        for listener in self._listeners:
            listener.start()

    def stop(self) -> None:
        self._listeners.clear()

    @staticmethod
    @abc.abstractmethod
    def _vk_code_mapper(vk_code) -> str:
        pass

    def _queue_is_open_for_business(self) -> bool:
        return not self.has_input() or self._allow_queue_buildup

    def _add_mouse_click_to_queue(self, x: int, y: int, button: Button, is_clicked: bool) -> None:
        mouse_button = mouse_button_parser[button]
        if self._queue_is_open_for_business():
            if is_clicked:
                self._ui_queue.put(SingleInput(InputType.MouseClick, (x, y, mouse_button)))
            # else:
            #     self._ui_queue.put(SingleInput(InputType.MouseRelease, (x, y, mouse_button)))

    def _add_mouse_scroll_to_queue(self, x, y, dx, dy):
        if self._queue_is_open_for_business():
            self._ui_queue.put(SingleInput(InputType.MouseScroll, (x, y, dx, dy)))

    def _add_key_press_to_queue(self, key: keyboard.Key) -> None:
        key_str = self._parse_pynput_key(key)
        if key_str in MODIFIERS:
            self._modifiers.add(key_str)
        else:
            key_str = "+".join(sorted(self._modifiers) + [key_str])
            # To avoid a situation of execution build up due to slow execution time
            if self._queue_is_open_for_business():
                self._ui_queue.put(SingleInput(InputType.KeyPress, key_str))

    def _add_key_release_to_queue(self, key: Union[keyboard.Key, str]) -> None:
        key_str = self._parse_pynput_key(key)
        if key_str in MODIFIERS:
            self._modifiers.discard(key_str)

    def _parse_pynput_key(self, key: Union[keyboard.Key, keyboard.KeyCode]) -> str:
        if str(key) == "<65437>":  # work around for a bug in pynput model that does not convert 5 for some reason
            key = "5"

        if hasattr(key, "vk") and key.vk is not None:
            key_str = self._vk_code_mapper(key.vk).lower()
        else:
            key_str = str(key).replace("'", "")
            key_str = key_str.replace("Key.", "")
            key_str = key_str.split("_", maxsplit=1)[0].lower()

        return key_str


class WindowsInputParser(BaseInputParser):
    @staticmethod
    def _vk_code_mapper(vk_code):
        return VK_CODE_MAP[vk_code]


class LinuxInputParser(BaseInputParser):
    @staticmethod
    def _vk_code_mapper(vk_code):
        return chr(vk_code)


class InputHandler:
    def __init__(self, window_name: str):
        self._keymap: Dict[str, KeyFunction] = {}
        self._keymap_description: Dict[str, list] = defaultdict(list)
        self._window_name = window_name

    def register_key_function(self, key_function: KeyFunction, callback_name: str) -> None:
        key = key_function.key
        if "+" in key:
            modifiers = sorted([modifier for modifier in key.split("+")[:-1] if modifier])
            key_without_modifiers = key.split("+")[-1] or "+"
            key = "+".join(modifiers + [key_without_modifiers])
        else:
            key_without_modifiers = key
            modifiers = []

        if key_without_modifiers.isnumeric():
            general_num_key = "+".join(modifiers + ["num"])
            if general_num_key in self._keymap:
                raise KeyError(f"{general_num_key} is registered: {self._keymap[general_num_key].description}")

        if key in self._keymap:
            raise KeyError(
                f"{key} is already registered (Registered action description: {self._keymap[key].description})"
            )

        self._keymap[key] = key_function
        if key_function.description:
            self._keymap_description[callback_name].append(f"{key:20.20}: {key_function.description:60.60}")

    def get_keymap_description(self) -> dict:
        return self._keymap_description

    def unregister_key_function(self, key: str) -> None:
        if key in self._keymap:
            del self._keymap[key]

    def handle_input(self, single_input: SingleInput) -> None:
        if single_input.input_type == InputType.KeyPress:
            self._handle_keypress(key_str=single_input.input_data)
        elif single_input.input_type == InputType.MouseScroll:
            self._handle_mouse_scroll(*single_input.input_data)

    def _handle_keypress(self, key_str):
        key_without_modifiers = key_str.split("+")[-1]
        if key_without_modifiers.isnumeric():
            general_num_key = key_str.replace(key_without_modifiers, "num")
        else:
            general_num_key = None

        if general_num_key in self._keymap:
            self._keymap[general_num_key].func(key_without_modifiers)
        elif key_str in self._keymap:
            self._keymap[key_str].func()
        else:
            print(f"{key_str} is not registered in the keymap")

    def _handle_mouse_scroll(self, x, y, dx, dy):
        if "mouse_scroll" not in self._keymap:
            return
        win_x, win_y, win_w, win_h = cv2.getWindowImageRect(self._window_name)
        curser_x = x - win_x
        curser_y = y - win_y
        if curser_x < 0 or curser_y < 0:
            return
        self._keymap["mouse_scroll"].func(curser_x, curser_y, dy)
