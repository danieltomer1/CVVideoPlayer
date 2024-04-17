import platform
import time
from typing import Optional, List
from functools import partial

import cv2
import numpy as np

from .input_manager import InputManager, SupportedOS
from .frame_editors import FrameInfoOverlay, FrameNormalizer, HistogramEqualizer, BaseFrameEditor
from .frame_reader import FrameReader
from .recorder import Recorder
from .utils.video_player_utils import (
    get_screen_adjusted_frame_size,
    KeyFunction,
    is_window_closed_by_mouse_click,
    get_screen_size, get_in_focus_window_id,
)


class VideoPlayer:
    def __init__(
        self,
        video_name: str,
        frame_reader: FrameReader,
        start_from_frame: int = 0,
        recorder: Optional[Recorder] = None,
        add_basic_frame_editors: bool = True,
    ):
        self._video_name = video_name
        self._frame_reader = frame_reader
        self._recorder = recorder

        self._last_frame = len(frame_reader) - 1
        self._frame_num = start_from_frame - 1
        self._current_system = SupportedOS(platform.system())
        self._screen_size = get_screen_size(self._current_system)

        self._current_frame = None
        self._frame_editors: List[BaseFrameEditor] = []

        self._play = False

        self._resize_factor = 1.0
        self._play_speed = 1
        self._exit = False

        if add_basic_frame_editors:
            self._add_basic_frame_editors()

        self._add_default_key_functions()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._recorder is not None:
            self._recorder.teardown()
        for frame_editor in self._frame_editors:
            frame_editor.teardown()

    def add_frame_editor(self, frame_editor: BaseFrameEditor) -> None:
        assert isinstance(frame_editor, BaseFrameEditor), "frame_editor must be a derived class of BaseFrameEditor"
        self._frame_editors.append(frame_editor)
        if frame_editor.key_function_to_register is not None:
            for key_function in frame_editor.key_function_to_register:
                assert isinstance(key_function, KeyFunction), (
                    f"{frame_editor.__class__.__name__} is trying to register a keymap action"
                    f" (key = {key_function.key}) which is not an instance of KeymapAction"
                )
                InputManager().register_key_function(key_function)

    def run(self) -> None:
        self._setup()

        InputManager().start()

        while not self._exit:

            key = InputManager().get_input()

            if is_window_closed_by_mouse_click(window_name=self._video_name):
                cv2.destroyAllWindows()
                break
            if key == "mouse_click":
                cv2.waitKey(30)
            elif get_in_focus_window_id(self._current_system) != self._window_id:
                continue
            else:
                InputManager().handle_key_str(key)
                self._show_current_frame()

        cv2.destroyAllWindows()

    def _setup(self) -> None:
        self._next_frame(1)
        for frame_editor in self._frame_editors:
            frame_editor.setup(self._current_frame)

        self._show_current_frame()
        time.sleep(0.5)  # make sure video player is up before checking the window id
        self._window_id = get_in_focus_window_id(self._current_system)
        cv2.waitKey(50)

    def _show_current_frame(self) -> None:
        frame = self._current_frame.copy()

        for frame_editor in self._frame_editors:
            if not frame_editor.edit_after_resize:
                shape_before_edit = frame.shape[:2]
                frame = frame_editor.edit_frame(frame, self._frame_num)
                assert (
                    frame.shape[:2] == shape_before_edit
                ), "frame editors with edit_after_resize==False can not alter the frame's shape"

        frame = self._resize_frame(frame)

        for frame_editor in self._frame_editors:
            if frame_editor.edit_after_resize:
                frame = frame_editor.edit_frame(frame, self._frame_num)

        frame = self._resize_frame(frame)

        if self._recorder is not None:
            self._recorder.write_frame_to_video(frame)

        cv2.imshow(winname=self._video_name, mat=frame)
        cv2.waitKey(10)
        cv2.waitKey(1)  # for some reason windows OS requires an additional waitKey to work properly

    def _add_basic_frame_editors(self) -> None:
        self.add_frame_editor(FrameInfoOverlay(video_total_frame_num=len(self._frame_reader)))
        self.add_frame_editor(FrameNormalizer())
        self.add_frame_editor(HistogramEqualizer())

    def _play_continuously(self) -> None:
        while (not InputManager().has_input()) and self._play:
            if self._play_speed > 0:
                self._next_frame(self._play_speed)
            else:
                self._prev_frame(-self._play_speed)
            self._show_current_frame()

    def _resize_frame(self, frame) -> np.ndarray:
        width, height = get_screen_adjusted_frame_size(
            screen_size=self._screen_size,
            frame_width=frame.shape[1],
            frame_height=frame.shape[0],
        )
        frame_size = int(self._resize_factor * width), int(self._resize_factor * height)
        return cv2.resize(frame, frame_size)

    def _next_frame(self, num_frames_to_skip=1) -> None:
        if self._frame_num == self._last_frame:
            self._play = False
            return

        self._frame_num = min(self._frame_num + num_frames_to_skip, self._last_frame)
        self._current_frame = self._frame_reader.get_frame(self._frame_num)

    def _prev_frame(self, num_frames_to_skip=1) -> None:
        if self._frame_num == 0:
            return

        self._frame_num = max(self._frame_num - num_frames_to_skip, 0)
        self._current_frame = self._frame_reader.get_frame(self._frame_num)

    def _change_frame_resize_factor(self, change_by: float) -> None:
        self._resize_factor = max(0.1, min(1.0, self._resize_factor + change_by))

    def _play_pause(self):
        self._play = not self._play
        self._play_continuously()

    def _increase_play_speed(self) -> None:
        if self._play_speed <= -1:
            self._play_speed = 1
        else:
            self._play_speed = min(16, self._play_speed * 2)

        self._play = True
        self._play_continuously()

    def _decrease_play_speed(self) -> None:
        if self._play_speed >= 1:
            self._play_speed = -1
        else:
            self._play_speed = max(-16, self._play_speed * 2)

        self._play = True
        self._play_continuously()

    def _on_exit(self) -> None:
        self._exit = True

    def _add_default_key_functions(self) -> None:
        default_key_functions = [
            KeyFunction("space", self._play_pause, "Play/Pause video"),
            KeyFunction("right", partial(self._next_frame, 1), "Next frame"),
            KeyFunction("left", partial(self._prev_frame, 1), "Previous frame"),
            KeyFunction("ctrl+right", partial(self._next_frame, 10), "10 frames forward"),
            KeyFunction("ctrl+left", partial(self._prev_frame, 10), "10 frames back"),
            KeyFunction("ctrl+shift+right", partial(self._next_frame, 50), "50 frames forward"),
            KeyFunction("ctrl+shift+left", partial(self._prev_frame, 50), "50 frames back"),
            KeyFunction("ctrl++", partial(self._change_frame_resize_factor, 0.1), "Increase frame size"),
            KeyFunction("ctrl+-", partial(self._change_frame_resize_factor, -0.1), "Decrease frame size"),
            KeyFunction("+", self._increase_play_speed, "Increase play speed"),
            KeyFunction("shift++", self._increase_play_speed, ""),
            KeyFunction("-", self._decrease_play_speed, "Decrease play speed"),
            KeyFunction("esc", self._on_exit, "Exit gracefully"),
        ]

        for key_function in default_key_functions:
            InputManager().register_key_function(key_function)
