import abc
from queue import Queue
from typing import Union

from pynput import keyboard, mouse
from pynput.mouse import Button

from ..utils.ui_utils import Singleton, SingleInput, mouse_button_parser, InputType, MODIFIERS


class BaseInputParser(metaclass=Singleton):
    def __init__(self, allow_queue_buildup=False):
        self._allow_queue_buildup = allow_queue_buildup
        self._ui_queue: Queue[SingleInput] = Queue()
        self._modifiers = set()
        self._listeners = []
        self._queue_is_blocked = False

    def pause(self):
        self._queue_is_blocked = True

    def resume(self):
        self._queue_is_blocked = False

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
        return not self._queue_is_blocked and (not self.has_input() or self._allow_queue_buildup)

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

        if str(key) == "<65032>":  # work around for a bug in pynput model that does not release shift
            key = "shift"

        if hasattr(key, "vk") and key.vk is not None:
            key_str = self._vk_code_mapper(key.vk).lower()
        else:
            key_str = str(key).replace("'", "")
            key_str = key_str.replace("Key.", "")
            key_str = key_str.split("_", maxsplit=1)[0].lower()

        return key_str
