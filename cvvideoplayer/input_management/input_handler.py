from collections import defaultdict
from typing import Dict, List

import cv2
from ..utils.video_player_utils import KeyFunction
from ..utils.ui_utils import SingleInput, InputType


class InputHandler:
    def __init__(self, window_name: str):
        self._keymap: Dict[str, List[KeyFunction]] = defaultdict(list)
        self._keymap_description: Dict[str, list] = defaultdict(list)
        self._window_name = window_name

    def register_key_function(self, key_function: KeyFunction, callback_name: str) -> None:
        self._keymap[key_function.key].append(key_function)
        if key_function.description:
            self._keymap_description[callback_name].append((key_function.key, key_function.description))

    def get_keymap_description(self) -> dict:
        return self._keymap_description

    def unregister_key_function(self, key: str, index: int) -> None:
        if key not in self._keymap:
            print(f"attempting to remove key={key} but it is not registered in keymap")
            return
        key_function_list = self._keymap[key]
        if len(key_function_list) <= index:
            print(f"attempting to remove index={index} from the key functions registered to key={key}"
                  f"the index is out of range")
        del self._keymap[key][index]

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
            for key_function in self._keymap[general_num_key]:
                key_function.func(key_without_modifiers)
        if key_str in self._keymap:
            for key_function in self._keymap[key_str]:
                key_function.func()
        if key_str not in self._keymap and general_num_key not in self._keymap:
            print(f"{key_str} is not registered in the keymap")

    def _handle_mouse_scroll(self, x, y, dx, dy):
        if "mouse_scroll" not in self._keymap:
            return
        win_x, win_y, win_w, win_h = cv2.getWindowImageRect(self._window_name)
        curser_x = x - win_x
        curser_y = y - win_y
        if curser_x < 0 or curser_y < 0:
            return
        self._keymap["mouse_scroll"][0].func(curser_x, curser_y, dy)
