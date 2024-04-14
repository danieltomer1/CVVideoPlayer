import dataclasses
from enum import Enum
from typing import Dict
from queue import Queue
import platform

from pynput import keyboard, mouse
from pynput._util import AbstractListener

from .utils.video_player_utils import (
    get_keyboard_layout,
    MODIFIERS,
    KeyFunction,

)
from .utils.windows_vk_dict import VK_CODE_MAP

class SupportedOS(Enum):
    LINUX = "Linux"
    WINDOWS = "Windows"

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

class InputManager(metaclass=Singleton):
    def __init__(self):
        self._keyboard_layout = get_keyboard_layout()
        assert self._keyboard_layout != "Hebrew", "Player Does not work with Hebrew keyboard layout"

        self._ui_queue = Queue()
        self._keymap: Dict[str,KeyFunction] = {}
        self._modifiers = set()
        self._current_system = SupportedOS(platform.system())
        self._map_vk_code = make_vk_code_mapper(self._current_system)
        self._listeners:list[AbstractListener] = []

    def register_key_function(self, key_function):
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

    def unregister_key_function(self, key):
        if key in self._keymap:
            del self._keymap[key]

    def has_input(self):
        return not self._ui_queue.empty()
    
    def get_input(self):
        key = None
        if self.has_input():
            key = self._ui_queue.get(block=False)
            if key not in MODIFIERS:
                key = self._handle_simple_key(key)
        if key is not None:
            self._keymap[key].func()
        return key

    def start(self):
        self._listeners.append(
            keyboard.Listener(
                on_press=self._add_key_press_to_queue,
                on_release=self._add_key_release_to_queue))
        self._listeners.append(
            mouse.Listener(
                on_click=self._add_mouse_click_to_queue
            ))
        
        for listener in self._listeners:
            listener.start()

    def stop(self):
        for listener in self._listeners:
            listener.stop()
        self._listeners.clear()

    def _add_mouse_click_to_queue(self,*_) -> None:
        if not self.has_input():
            self._add_key_press_to_queue("mouse_click")

    def _add_key_press_to_queue(self, key) -> None:
        if key in MODIFIERS:
            key = str(key).replace("Key.", "").split("_", maxsplit=1)[0]
            if key not in self._modifiers:
                self._modifiers.add(key)

        elif not self.has_input():  # To avoid a situation of execution build up due to slow execution time
            self._ui_queue.put(key)

    def _add_key_release_to_queue(self, key) -> None:
        if key in MODIFIERS:
            key = str(key).replace("Key.", "").split("_", maxsplit=1)[0]
            if str(key) in self._modifiers:
                self._modifiers.remove(key)

    def get_keymap_description(self) -> str:
        result = "Keymap:\n"
        for key, key_function in self._keymap.items():
            if key_function.description:
                result += f"\t{key:20} {key_function.description}\n"
        return result

    def print_keymap(self):
        print(self.get_keymap_description())

    def clone_keymap(self):
        return {key: dataclasses.replace(key_function) for key, key_function in self._keymap.items()}

    def _handle_simple_key(self, key):
        if str(key) == "<65437>":  # work around for a bug in pynput model that does not convert 5 for some reason
            key = "5"

        if hasattr(key, "vk") and key.vk is not None:
            key = self._map_vk_code(key.vk).lower()
        else:
            key = str(key).replace("'", "").replace("Key.", "")

        if str(key).isnumeric():
            general_num_key = "+".join(sorted(self._modifiers) + ["num"])
        else:
            general_num_key = None

        key = "+".join(sorted(self._modifiers) + [key])

        if general_num_key in self._keymap:
            return general_num_key
        if key in self._keymap:
            return key
        
        print(f"Warning: {key} is not registered in the keymap")
        return None
