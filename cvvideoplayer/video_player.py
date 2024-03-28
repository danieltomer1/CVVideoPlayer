import platform
from queue import Queue
from typing import *

import Xlib.display
import cv2
from pynput import keyboard, mouse

from .frame_editors import AbstractFrameEditor, FrameNumPrinter, FrameNormalizer, HistogramEqualizer
from .frame_reader import AbstractFrameReader
from .recorder import Recorder
from .utils.video_player_utils import (
    get_keyboard_layout,
    get_screen_adjusted_frame_size,
    get_screen_size,
    get_forground_window_pid,
    KeymapAction,
)
from .utils.windows_vk_dict import VK_CODE_MAP


class VideoPlayer:
    def __init__(
        self,
        video_name: str,
        frame_reader: AbstractFrameReader,
        start_from_frame: int = 0,
        recorder: Optional[Recorder] = None,
        add_basic_frame_editors: bool = True,
    ):

        self._video_name = video_name
        self._frame_reader = frame_reader
        self._recorder = recorder

        self._show_sidebar = False
        self._start_from_frame = start_from_frame
        self._last_frame = len(frame_reader) - 1
        self._frame_num = start_from_frame - 1
        self._modifiers = set()
        self._current_frame = None
        self._frame_editors: list[AbstractFrameEditor] = []

        self._ui_queue = Queue()
        self._keyboard_layout = get_keyboard_layout()
        self._number_action_registered = False
        self._play = False

        self._screen_size = get_screen_size()
        self._resize_factor = 1.0

        self._keymap = self._create_basic_keymap()
        self._next_frame(1)
        if add_basic_frame_editors:
            self._add_basic_frame_editors()

        if platform.system() == "Linux":
            self._linux_setup()
        elif platform.system() == "Windows":
            self._windows_setup()
        else:
            raise NotImplementedError(f"{platform.system()=} not supported")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._recorder is not None:
            self._recorder.teardown()
        for frame_editor in self._frame_editors:
            frame_editor.teardown()

    def add_frame_editor(self, frame_editor: AbstractFrameEditor):
        frame_editor.setup(self._current_frame)
        self._frame_editors.append(frame_editor)
        if frame_editor.keymap_actions_to_register is not None:
            for key, action in frame_editor.keymap_actions_to_register.items():
                assert isinstance(
                    action, KeymapAction
                ), f"{frame_editor.__class__.__name__} is trying to register a keymap action (key = {key}) which is not an instance of KeymapAction"
                self.register_keymap_action(key, action.func, action.description)

    def add_frame_num_printer(self):
        frame_num_printer = FrameNumPrinter(video_total_frame_num=len(self._frame_reader))
        self.add_frame_editor(frame_num_printer)

    def add_frame_normalizer(self):
        frame_normalizer = FrameNormalizer()
        self.add_frame_editor(frame_normalizer)

    def add_histogram_equalizer(self):
        histogram_equalizer = HistogramEqualizer()
        self.add_frame_editor(histogram_equalizer)

    def register_keymap_action(self, key: str, func: Callable, desc: str):
        assert (
            "right" not in key and "left" not in key and "space" not in key
        ), "right and left and space are reserved for video playing"
        if "+" in key:
            modifiers = sorted(key.split("+")[:-1])
            key_without_modifiers = key.split("+")[-1]
            key = "+".join(modifiers + [key_without_modifiers])
        else:
            key_without_modifiers = key
            modifiers = []

        general_num_key = "+".join(modifiers + ["num"])
        if key_without_modifiers.isnumeric() and general_num_key in self._keymap:
            raise KeyError(f"{general_num_key} is registered: {self._keymap[general_num_key].description}")

        if key in self._keymap:
            raise KeyError(
                f"{key} is already registered (Registered action description: {self._keymap[key].description})"
            )

        self._keymap[key] = KeymapAction(func, desc)

    def register_keymap_general_number_action(
        self,
        func,
        desc,
        modifiers: Tuple = (),
    ):
        key = "+".join(modifiers + ("num",))
        if key in self._keymap:
            raise KeyError(
                f"{key} is already registered (Registered action description: {self._keymap[key].description})"
            )
        self._keymap[key] = KeymapAction(func, desc)

    def run(self):
        self._show_current_frame()
        cv2.waitKey(30)
        self._print_keymap()

        keyboard.Listener(
            on_press=self._add_key_press_to_queue,
            on_release=self._add_key_release_to_queue,
        ).start()

        mouse.Listener(on_click=self._add_mouse_click_to_queue).start()

        while True:
            action, cur_key = self._ui_queue.get()
            if action == "mouse_click":
                cv2.waitKey(30)
            if cv2.getWindowProperty(self._video_name, cv2.WND_PROP_VISIBLE) < 1:
                break
            if cur_key == keyboard.Key.esc:
                cv2.destroyAllWindows()
                break
            if action == "press":
                if cur_key == keyboard.Key.space:
                    self._play = bool(1 - self._play)
                    self._play_continuously()
                else:
                    self._handle_keyboard_press(cur_key)
            if action == "release":
                self._handle_keyboard_release(cur_key)

    def _windows_setup(self):
        self._window_pid = get_forground_window_pid()
        self._get_in_focus_window_name = get_forground_window_pid
        self._map_vk_code = lambda x: VK_CODE_MAP[x]

    def _linux_setup(self):
        self._window_pid = self._video_name
        self._map_vk_code = lambda x: chr(x)

        def _get_in_focus_window_name():
            window = Xlib.display.Display().get_input_focus().focus
            if isinstance(window, int):
                return ""
            return window.get_wm_name()

        self._get_in_focus_window_name = _get_in_focus_window_name

    def _add_key_press_to_queue(self, key):

        if self._get_in_focus_window_name() != self._window_pid:
            return

        if self._keyboard_layout == "Hebrew":
            self._keyboard_layout = get_keyboard_layout()
            print("Studio Does not work with Hebrew keyboard layout, switch to English to continue")
            return

        if key in {
            keyboard.Key.ctrl,
            keyboard.Key.ctrl_r,
            keyboard.Key.ctrl_l,
            keyboard.Key.alt,
            keyboard.Key.alt_r,
            keyboard.Key.alt_l,
            keyboard.Key.shift,
            keyboard.Key.shift_r,
            keyboard.Key.shift_l,
        }:
            key = str(key).replace("Key.", "").split("_")[0]
            if key not in self._modifiers:
                self._modifiers.add(key)

        elif self._ui_queue.empty():  # To avoid a situation of execution build up due to slow execution time
            self._ui_queue.put(("press", key))

    def _add_key_release_to_queue(self, key):
        if key in {
            keyboard.Key.ctrl,
            keyboard.Key.ctrl_r,
            keyboard.Key.ctrl_l,
            keyboard.Key.alt,
            keyboard.Key.alt_r,
            keyboard.Key.alt_l,
            keyboard.Key.shift,
            keyboard.Key.shift_r,
            keyboard.Key.shift_l,
        }:
            key = str(key).replace("Key.", "").split("_")[0]
            if str(key) in self._modifiers:
                self._modifiers.remove(key)
            return

        if not self._get_in_focus_window_name() == self._video_name:
            return

        if key == keyboard.Key.space:
            return
        self._ui_queue.put(("release", key))

    def _add_mouse_click_to_queue(self, x, y, button, pressed):
        if self._ui_queue.empty():
            self._ui_queue.put(("mouse_click", (x, y, button, pressed)))

    def _add_basic_frame_editors(self):
        self.add_frame_num_printer()
        self.add_frame_normalizer()
        self.add_histogram_equalizer()

    def _print_keymap(self):
        print("space bar: Play/Pause video")
        for key, action in self._keymap.items():
            print(f"{key}: {action.description}")
        print("***********************************")

    def _play_continuously(self):
        while self._ui_queue.empty() and self._play:
            self._next_frame(1)
            self._show_current_frame()

    def _resize_frame(self, frame):
        width, height = get_screen_adjusted_frame_size(
            screen_size=self._screen_size,
            frame_width=frame.shape[1],
            frame_height=frame.shape[0],
        )
        frame_size = int(self._resize_factor * width), int(self._resize_factor * height)
        return cv2.resize(frame, frame_size)

    def _show_current_frame(self):
        frame = self._current_frame.copy()

        for frame_editor in self._frame_editors:
            if not frame_editor.edit_after_resize:
                frame = frame_editor.edit_frame(frame, self._frame_num)

        frame = self._resize_frame(frame)

        for frame_editor in self._frame_editors:
            if frame_editor.edit_after_resize:
                frame = frame_editor.edit_frame(frame, self._frame_num)

        frame = self._resize_frame(frame)

        if self._recorder is not None:
            self._recorder.write_frame_to_video(frame)

        cv2.imshow(winname=self._video_name, mat=frame)
        cv2.waitKey(5)

    def _next_frame(self, num_frames_to_skip=1):
        if self._frame_num == self._last_frame:
            return

        self._frame_num = min(self._frame_num + num_frames_to_skip, len(self._frame_reader) - 1)
        self._current_frame = self._frame_reader.get_frame(self._frame_num)

    def _prev_frame(self, num_frames_to_skip=1):
        if self._frame_num == 0:
            return

        self._frame_num = max(self._frame_num - num_frames_to_skip, 0)
        self._current_frame = self._frame_reader.get_frame(self._frame_num)

    def _change_frame_resize_factor(self, change_by: float):
        self._resize_factor = max(0.1, min(1.0, self._resize_factor + change_by))

    def _create_basic_keymap(self) -> Dict[str, KeymapAction]:
        keymap = {
            "right": KeymapAction(func=lambda: self._next_frame(1), description="Go to next frame"),
            "left": KeymapAction(func=lambda: self._prev_frame(1), description="Go to previous frame"),
            "ctrl+right": KeymapAction(func=lambda: self._next_frame(10), description="Go 10 frames forward"),
            "ctrl+left": KeymapAction(func=lambda: self._prev_frame(10), description="Go 10 frames back"),
            "ctrl+shift+right": KeymapAction(func=lambda: self._next_frame(50), description="Go 50 frames forward"),
            "ctrl+shift+left": KeymapAction(func=lambda: self._prev_frame(50), description="Go 50 frames back"),
            "+": KeymapAction(func=lambda: self._change_frame_resize_factor(0.1), description="Increase frame size"),
            "shift++": KeymapAction(
                func=lambda: self._change_frame_resize_factor(0.1), description="Increase frame size"
            ),
            "-": KeymapAction(func=lambda: self._change_frame_resize_factor(-0.1), description="Decrease frame size"),
        }
        return keymap

    def _handle_keyboard_press(self, key_without_modifiers):
        if (
            str(key_without_modifiers) == "<65437>"
        ):  # work around for a bug in pynput model that does not convert 5 for some reason
            key_without_modifiers = "5"

        if hasattr(key_without_modifiers, "vk") and key_without_modifiers.vk is not None:
            key_without_modifiers = self._map_vk_code(key_without_modifiers.vk).lower()
            key = "+".join(sorted(self._modifiers) + [key_without_modifiers])
        else:
            key_without_modifiers = str(key_without_modifiers).replace("'", "").replace("Key.", "")
            key = "+".join(sorted(self._modifiers) + [key_without_modifiers])

        if str(key_without_modifiers).isnumeric():
            general_num_key = "+".join(sorted(self._modifiers) + ["num"])
        else:
            general_num_key = None

        if general_num_key in self._keymap:
            self._keymap[general_num_key].func(key_without_modifiers)
        elif key in self._keymap:
            self._keymap[key].func()
        else:
            print(f"{key} deos nothing")

        self._show_current_frame()

    def _handle_keyboard_release(self, key):
        pass
