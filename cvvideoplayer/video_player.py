import abc
import ctypes
import subprocess
import time
from pathlib import Path
from queue import Empty
from typing import Optional, List, Union
from functools import partial

import Xlib
import cv2
import numpy as np

from .input_management import InputHandler, WindowsInputParser, LinuxInputParser
from .frame_editors import BaseFrameEditCallback
from .frame_reader import FrameReader
from .recorder import AbstractRecorder
from .utils.video_player_utils import (
    get_screen_adjusted_frame_size,
    KeyFunction,
    is_window_closed_by_mouse_click,
    get_frame_reader,
    get_recorder,
    CURRENT_OS,
    SupportedOS,
)


class DeprecatedVideoPlayer:
    def __init__(
        self,
        video_source: Union[str, Path, FrameReader],
        start_from_frame: int = 0,
        frame_edit_callbacks: Optional[List[BaseFrameEditCallback]] = None,
        record: Union[bool, AbstractRecorder] = False
    ):
        self.per_os_video_player = create_video_player(
            video_source=video_source,
            start_from_frame=start_from_frame,
            frame_edit_callbacks=frame_edit_callbacks,
            record=record,
        )

    def run(self) -> None:
        self.per_os_video_player.run()


class VideoPlayer(abc.ABC):
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
        self.input_handler = InputHandler()
        self._recorder = get_recorder(record)
        self._last_frame = len(self.frame_reader) - 1
        self._current_frame_num = start_from_frame - 1
        self._screen_size = self._get_screen_size()
        self._screen_adjusted_frame_size = None
        self._original_frame_size = None
        self._current_frame = None
        self._frame_edit_callbacks = frame_edit_callbacks or []

        self._play = False

        self._zoom_factor = 1.0
        self._zoom_crop = None
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
        self._input_parser.stop()

    def run(self) -> None:
        try:
            self._setup()
            self._input_parser.start()
            self._run_player_loop()
        finally:
            self.__exit__()

    @staticmethod
    @abc.abstractmethod
    def _get_screen_size():
        pass

    @abc.abstractmethod
    def _get_in_focus_window_id(self):
        pass

    @property
    @abc.abstractmethod
    def _input_parser(self):
        pass

    def _run_player_loop(self):
        while not self._exit:
            if self._get_in_focus_window_id() != self._window_id:
                if is_window_closed_by_mouse_click(window_name=self._window_name):
                    break
                else:
                    cv2.waitKey(20)
                    continue
            try:
                single_input = self._input_parser.get_input()
            except Empty:
                cv2.waitKey(1)
                continue
            self.input_handler.handle_input(single_input)
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
                self.input_handler.register_key_function(key_function, callback.__class__.__name__)

            callback.setup(self, self._current_frame)

    def _setup(self) -> None:
        self._change_current_frame(change_by=1)
        self._setup_callbacks()
        self._screen_adjusted_frame_size = get_screen_adjusted_frame_size(
            screen_size=self._screen_size,
            frame_width=self._current_frame.shape[1],
            frame_height=self._current_frame.shape[0],
        )
        self._original_frame_size = tuple(self._current_frame.shape[:2][::-1])
        self._zoom_crop = (0, 0, self._original_frame_size[0], self._original_frame_size[1])
        self._show_current_frame()
        time.sleep(0.5)  # make sure video player is up before checking the window id
        self._window_id = self._get_in_focus_window_id()
        cv2.waitKey(50)

    def _show_current_frame(self) -> None:
        frame = self._current_frame.copy()

        for callback in self._frame_edit_callbacks:
            if not callback.enabled:
                continue
            shape_before_edit = frame.shape[:2]
            frame = callback.before_frame_resize(self, frame, self._current_frame_num)
            assert frame.shape[:2] == shape_before_edit, "callbacks can not alter the frame's shape before resize"

        frame = self._crop_and_resize_frame(frame)

        for callback in self._frame_edit_callbacks:
            if not callback.enabled:
                continue
            frame = callback.after_frame_resize(self, frame, self._current_frame_num)

        #  we resize again in case frame size has been changed in "after_frame_resize" hooks
        if frame.shape[0] != self._screen_adjusted_frame_size[1] or frame.shape[1] != self._screen_adjusted_frame_size[0]:
            frame = cv2.resize(frame, self._screen_adjusted_frame_size)

        if self._recorder is not None:
            self._recorder.write_frame_to_video(self, frame, self._current_frame_num)
        cv2.imshow(winname=self._window_name, mat=frame)
        cv2.waitKey(1)

    def _play_continuously(self) -> None:
        while (not self._input_parser.has_input()) and self._play and not self._exit:
            self._change_current_frame(change_by=self._play_speed)
            self._show_current_frame()

    def _crop_and_resize_frame(self, frame) -> np.ndarray:
        frame = frame[
                self._zoom_crop[1]: self._zoom_crop[1] + self._zoom_crop[3],
                self._zoom_crop[0]: self._zoom_crop[0] + self._zoom_crop[2],
                ]
        frame = cv2.resize(frame, self._screen_adjusted_frame_size)
        return frame

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

    def _set_zoom(self, curser_x: int, curser_y: int, scroll_direction: int):
        new_zoom_factor = max(1.0, min(5.0, self._zoom_factor + 0.5 * scroll_direction))
        if new_zoom_factor != self._zoom_factor:
            self._zoom_factor = new_zoom_factor
            adjusted_width, adjusted_height = self._screen_adjusted_frame_size
            norm_curser_position = (curser_x / adjusted_width, curser_y / adjusted_height)
            w = h = 1 / self._zoom_factor
            x_min = norm_curser_position[0] * (1 - w)
            y_min = norm_curser_position[1] * (1 - h)
            self._zoom_crop = (
                int(self._original_frame_size[0] * x_min),
                int(self._original_frame_size[1] * y_min),
                int(self._original_frame_size[0] * w),
                int(self._original_frame_size[1] * h)
            )

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
            KeyFunction("esc", self._set_exit_to_true, "Exit gracefully"),
            KeyFunction("mouse_scroll", self._set_zoom, "zoom in and out"),
        ]

        for key_function in default_key_functions:
            self.input_handler.register_key_function(key_function, "Video Control")


class WindowsVideoPlayer(VideoPlayer):
    def __init__(self, **video_player_kwargs):
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
        super().__init__(**video_player_kwargs)

    def _show_current_frame(self) -> None:
        super()._show_current_frame()
        cv2.waitKey(1)  # for some reason Windows OS requires an additional waitKey to work properly

    @property
    def _input_parser(self):
        return WindowsInputParser()

    @staticmethod
    def _get_screen_size():
        user32 = ctypes.windll.user32
        screensize = 0.9 * user32.GetSystemMetrics(0), 0.9 * user32.GetSystemMetrics(1)
        return screensize

    def _get_in_focus_window_id(self):
        h_wnd = ctypes.windll.user32.GetForegroundWindow()
        pid = ctypes.wintypes.DWORD()
        ctypes.windll.user32.GetWindowThreadProcessId(h_wnd, ctypes.byref(pid))
        return pid.value
    pass


class LinuxVideoPlayer(VideoPlayer):
    def __init__(self, **video_player_kwargs):
        super().__init__(**video_player_kwargs)
        self._display = Xlib.display.Display()

    @property
    def _input_parser(self):
        return LinuxInputParser()

    def _get_in_focus_window_id(self):
        window = self._display.get_input_focus().focus
        if isinstance(window, int):
            return ""
        return window.id

    @staticmethod
    def _get_screen_size():
        try:
            screen_size_str = (
                subprocess.check_output('xrandr | grep "\*" | cut -d" " -f4', shell=True).decode().strip().split("\n")[
                    0]
            )
            screen_w, screen_h = screen_size_str.split("x")
            screen_w = 0.9 * int(screen_w)
            screen_h = 0.9 * int(screen_h)
            return screen_w, screen_h
        except (ValueError, TypeError, subprocess.CalledProcessError, IndexError):
            return None, None


def create_video_player(**video_kwargs) -> VideoPlayer:
    if CURRENT_OS == SupportedOS.WINDOWS:
        return WindowsVideoPlayer(**video_kwargs)
    elif CURRENT_OS == SupportedOS.LINUX:
        return LinuxVideoPlayer(**video_kwargs)
