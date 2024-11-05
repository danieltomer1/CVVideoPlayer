import platform
import time
from pathlib import Path
from typing import Optional, List, Union
from functools import partial

import cv2
import numpy as np

from .input_manager import InputManager, SupportedOS
from .frame_editors import BaseFrameEditCallback
from .frame_reader import FrameReader
from .recorder import AbstractRecorder
from .utils.video_player_utils import (
    get_screen_adjusted_frame_size,
    KeyFunction,
    is_window_closed_by_mouse_click,
    get_screen_size,
    get_in_focus_window_id,
    get_frame_reader,
    get_recorder,
)


class VideoPlayer:
    def __init__(
        self,
        video_source: Union[str, Path, FrameReader],
        start_from_frame: int = 0,
        frame_edit_callbacks: Optional[List[BaseFrameEditCallback]] = None,
        record: Union[bool, AbstractRecorder] = False,
    ):
        """
        Params:
        - video_source : Union[str, Path, FrameReader] The source of the video to be played. It can be a file path, a
         directory path, or a FrameReader instance.
        - start_from_frame : int, optional The frame number to start the video from (default is 0).
        - frame_edit_callbacks : list, optional A list of frame editing callbacks (default is None).
         Each callback must be an instance of BaseFrameEditCallback.
        - record : Union[bool, AbstractRecorder], optional Whether to record the video or not (default is False).
        It can also be an instance of AbstractRecorder for custom recording functionality.
        """
        self.frame_reader = get_frame_reader(video_source)
        self._recorder = get_recorder(record)
        self._last_frame = len(self.frame_reader) - 1
        self._current_frame_num = start_from_frame - 1
        self._current_system = SupportedOS(platform.system())
        self._screen_size = get_screen_size(self._current_system)

        self._current_frame = None
        self._frame_edit_callbacks = frame_edit_callbacks

        self._play = False

        self._resize_factor = 1.0
        self._play_speed = 1
        self._exit = False
        self._window_name = "CVvideoPlayer"
        self._add_default_key_functions()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        cv2.destroyAllWindows()
        if self._recorder is not None:
            self._recorder.teardown()
        for callback in self._frame_edit_callbacks:
            callback.teardown()
        InputManager().stop()

    def run(self) -> None:
        try:
            self._setup()
            InputManager().start()
            self._run_player_loop()
        finally:
            self.__exit__()

    def _run_player_loop(self):
        while not self._exit:
            key = InputManager().get_input()
            if is_window_closed_by_mouse_click(window_name=self._window_name):
                cv2.waitKey(5)
                break
            elif get_in_focus_window_id(self._current_system) != self._window_id:
                continue
            else:
                InputManager().handle_key_str(key)
                self._play_continuously() if self._play else self._show_current_frame()

    def _setup_callbacks(self):
        for callback in self._frame_edit_callbacks:
            assert isinstance(callback, BaseFrameEditCallback), (
                "frame_editor must be a derived class of" " BaseFrameEditor"
            )
            for key_function in callback.key_function_to_register:
                assert isinstance(key_function, KeyFunction), (
                    f"{callback.__class__.__name__} is trying to register a key function"
                    f" (key = {key_function.key}) which is not an instance of KeyFunction"
                )
                InputManager().register_key_function(key_function, callback.__class__.__name__)

            callback.setup(self, self._current_frame)

    def _setup(self) -> None:
        self._change_current_frame(change_by=1)
        self._setup_callbacks()
        self._show_current_frame()
        time.sleep(0.5)  # make sure video player is up before checking the window id
        self._window_id = get_in_focus_window_id(self._current_system)
        cv2.waitKey(50)

    def _show_current_frame(self) -> None:
        frame = self._current_frame.copy()

        for callback in self._frame_edit_callbacks:
            if not callback.enabled:
                continue
            shape_before_edit = frame.shape[:2]
            frame = callback.before_frame_resize(self, frame, self._current_frame_num)
            assert frame.shape[:2] == shape_before_edit, "callbacks can not alter the frame's shape before resize"

        frame = self._resize_frame(frame)

        for callback in self._frame_edit_callbacks:
            if not callback.enabled:
                continue
            frame = callback.after_frame_resize(self, frame, self._current_frame_num)

        frame = self._resize_frame(frame)

        if self._recorder is not None:
            self._recorder.write_frame_to_video(frame)
        cv2.imshow(winname=self._window_name, mat=frame)
        cv2.waitKey(10)
        cv2.waitKey(1)  # for some reason Windows OS requires an additional waitKey to work properly

    def _play_continuously(self) -> None:
        while (not InputManager().has_input()) and self._play:
            self._change_current_frame(change_by=self._play_speed)
            self._show_current_frame()

    def _resize_frame(self, frame) -> np.ndarray:
        width, height = get_screen_adjusted_frame_size(
            screen_size=self._screen_size,
            frame_width=frame.shape[1],
            frame_height=frame.shape[0],
        )
        frame_size = int(self._resize_factor * width), int(self._resize_factor * height)
        return cv2.resize(frame, frame_size)

    def _change_current_frame(self, change_by: int) -> None:
        if change_by > 0 and self._current_frame_num == self._last_frame:
            self._play = False
            return

        if change_by < 0 and self._current_frame_num == 0:
            return

        self._current_frame_num = max(0, min(self._current_frame_num + change_by, self._last_frame))
        self._current_frame = self.frame_reader.get_frame(self._current_frame_num)

    def _pause_and_change_current_frame(self, change_by: int) -> None:
        self._play = False
        self._change_current_frame(change_by)

    def _change_frame_resize_factor(self, change_by: float) -> None:
        self._resize_factor = max(0.1, min(1.0, self._resize_factor + change_by))

    def _play_pause(self):
        self._play = not self._play

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

    def _set_exit_to_true(self):
        self._exit = True

    def _add_default_key_functions(self) -> None:
        default_key_functions = [
            KeyFunction("space", self._play_pause, "Play/Pause video"),
            KeyFunction("right", partial(self._pause_and_change_current_frame, 1), "Next frame"),
            KeyFunction("left", partial(self._pause_and_change_current_frame, -1), "Previous frame"),
            KeyFunction("ctrl+right", partial(self._pause_and_change_current_frame, 10), "10 frames forward"),
            KeyFunction("ctrl+left", partial(self._pause_and_change_current_frame, -10), "10 frames back"),
            KeyFunction("ctrl+shift+right", partial(self._pause_and_change_current_frame, 50), "50 frames forward"),
            KeyFunction("ctrl+shift+left", partial(self._pause_and_change_current_frame, -50), "50 frames back"),
            KeyFunction("+", partial(self._change_frame_resize_factor, 0.1), "Increase frame size"),
            KeyFunction("ctrl+=", partial(self._change_frame_resize_factor, 0.1), ""),
            KeyFunction("shift++", partial(self._change_frame_resize_factor, 0.1), ""),
            KeyFunction("=", partial(self._change_frame_resize_factor, 0.1), ""),
            KeyFunction("-", partial(self._change_frame_resize_factor, -0.1), "Decrease frame size"),
            KeyFunction("esc", self._set_exit_to_true, "Exit gracefully"),
        ]

        for key_function in default_key_functions:
            InputManager().register_key_function(key_function, "Video Control")
