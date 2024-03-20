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

        self._keyboard_layout = get_keyboard_layout()
        self._number_action_registered = False
        self._play = False
        self._display = Xlib.display.Display() if platform.system() == "Linux" else None

        self._screen_size = get_screen_size()
        self._keymap = self._create_basic_keymap()
        self._next_frame(1)
        if add_basic_frame_editors:
            self._add_basic_frame_editors()
        self._show_current_frame()
        self._window_pid = get_forground_window_pid() if platform.system() == "Windows" else self._video_name

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
        self._show_current_frame()

    def add_frame_num_printer(self, key="ctrl+f"):
        frame_num_printer = FrameNumPrinter()
        self.add_frame_editor(frame_num_printer)
        self.register_keymap_action(
            key=key,
            func=frame_num_printer.enable_disable,
            desc="enable/disable frame number print",
        )

    def add_frame_normalizer(self, set_range_key="ctrl+r", show_histogram_key="ctrl+alt+r"):
        frame_normalizer = FrameNormalizer()
        self.add_frame_editor(frame_normalizer)
        self.register_keymap_action(
            key=set_range_key,
            func=frame_normalizer.set_dynamic_range,
            desc="set dynamic range",
        )

        self.register_keymap_action(
            key=show_histogram_key,
            func=frame_normalizer.show_frame_histogram,
            desc="show frame histogram",
        )

    def add_histogram_equalizer(self, key="ctrl+h"):
        histogram_equalizer = HistogramEqualizer()
        self.add_frame_editor(histogram_equalizer)
        self.register_keymap_action(
            key=key,
            func=histogram_equalizer.enable_disable,
            desc="enable/disable histogram equalization",
        )

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

    def _get_in_focus_window_name(self):
        if platform.system() == "Linux":
            window = self._display.get_input_focus().focus
            if isinstance(window, int):
                return ""
            return window.get_wm_name()

        elif platform.system() == "Windows":
            return get_forground_window_pid()

    def run(self):
        self._print_keymap()
        queue = Queue()

        def on_press(key):

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

            elif queue.empty():  # To avoid a situation of execution build up due to slow execution time
                queue.put(("press", key))

        def on_release(key):
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
            queue.put(("release", key))

        def on_mouse_click(x, y, button, pressed):
            if queue.empty():  # To avoid a situation of execution build up due to slow execution time
                queue.put(("mouse_click", (x, y, button, pressed)))

        listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        listener_mouse = mouse.Listener(on_click=on_mouse_click)
        listener.start()
        listener_mouse.start()

        while True:
            action, cur_key = queue.get()
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
                    self._play_continuously(queue)
                else:
                    self._handle_keyboard_press(cur_key)
            if action == "release":
                self._handle_keyboard_release(cur_key)

    def _add_basic_frame_editors(self):
        self.add_frame_num_printer()
        self.add_frame_normalizer()
        self.add_histogram_equalizer()

    def _print_keymap(self):
        print("space bar: Play/Pause video")
        for key, action in self._keymap.items():
            print(f"{key}: {action.description}")
        print("***********************************")

    def _play_continuously(self, queue):
        while queue.empty() and self._play:
            self._next_frame(1)

    def _resize_frame_to_fit_screen(self, frame):
        adjusted_size = get_screen_adjusted_frame_size(
            screen_size=self._screen_size,
            frame_width=frame.shape[1],
            frame_height=frame.shape[0],
        )

        return cv2.resize(frame, adjusted_size)

    def _show_current_frame(self):
        frame = self._current_frame.copy()

        for frame_editor in self._frame_editors:
            if not frame_editor.edit_after_resize:
                frame = frame_editor.edit_frame(frame, self._frame_num)

        frame = self._resize_frame_to_fit_screen(frame)

        for frame_editor in self._frame_editors:
            if frame_editor.edit_after_resize:
                frame = frame_editor.edit_frame(frame, self._frame_num)

        frame = self._resize_frame_to_fit_screen(frame)

        if self._recorder is not None:
            self._recorder.write_frame_to_video(frame)

        cv2.imshow(winname=self._video_name, mat=frame)
        cv2.waitKey(5)
        cv2.waitKey(1)

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

    def _create_basic_keymap(self) -> Dict[str, KeymapAction]:
        keymap = {
            "right": KeymapAction(func=lambda: self._next_frame(1), description="Go to next frame"),
            "left": KeymapAction(func=lambda: self._prev_frame(1), description="Go to previous frame"),
            "ctrl+right": KeymapAction(func=lambda: self._next_frame(10), description="Go 10 frames forward"),
            "ctrl+left": KeymapAction(func=lambda: self._prev_frame(10), description="Go 10 frames back"),
            "ctrl+shift+right": KeymapAction(func=lambda: self._next_frame(50), description="Go 50 frames forward"),
            "ctrl+shift+left": KeymapAction(func=lambda: self._prev_frame(50), description="Go 50 frames back"),
        }
        return keymap

    def _handle_keyboard_press(self, key_without_modifiers):
        if (
            str(key_without_modifiers) == "<65437>"
        ):  # work around for a bug in pynput model that does not convert 5 for some reason
            key_without_modifiers = "5"

        if hasattr(key_without_modifiers, "vk"):
            key_without_modifiers = chr(key_without_modifiers.vk).lower()

        key_without_modifiers = str(key_without_modifiers).replace("'", "").replace("Key.", "")

        if str(key_without_modifiers).isnumeric():
            general_num_key = "+".join(sorted(self._modifiers) + ["num"])
        else:
            general_num_key = None

        key = "+".join(sorted(self._modifiers) + [key_without_modifiers])

        if general_num_key in self._keymap:
            action = self._keymap[general_num_key]
            action.func(key_without_modifiers)
        else:
            action = self._keymap.get(key, KeymapAction(func=lambda: print(f"{key} deos nothing"), description=""))
            action.func()

        self._show_current_frame()

    def _handle_keyboard_release(self, key):
        pass
