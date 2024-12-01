import abc
from pathlib import Path
from queue import Empty
from typing import Optional, List, Union
from functools import partial

import cv2
import numpy as np

from ..display_managers.abstract_display_manager import DisplayManager
from ..frame_editors import (
    BaseFrameEditCallback,
    FitFrameToScreen,
    FrameInfoOverlay,
    KeyMapOverlay,
)
from ..frame_reader import FrameReader
from ..input_management.base_input_parser import BaseInputParser
from ..input_management.input_handler import InputHandler
from ..recorder import AbstractRecorder
from ..utils.video_player_utils import (
    calc_screen_adjusted_frame_size,
    KeyFunction,
    is_window_closed_by_mouse_click,
    get_frame_reader,
    get_recorder,
)


class VideoPlayer(abc.ABC):
    def __init__(
        self,
        video_source: Union[str, Path, FrameReader],
        display_manager: DisplayManager,
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
        self._window_name = "CVvideoPlayer"
        self._display_manager = display_manager
        self.frame_reader = get_frame_reader(video_source)
        self.input_handler = InputHandler(self._window_name)
        self._recorder = get_recorder(record)

        self._last_frame = len(self.frame_reader) - 1
        self._current_frame_num = start_from_frame

        self._screen_size = self._display_manager.get_screen_size()
        self._original_frame_size = None

        self._frame_edit_callbacks = frame_edit_callbacks
        if self._frame_edit_callbacks is None:
            self._frame_edit_callbacks = [
                FitFrameToScreen(),
                FrameInfoOverlay(),
                KeyMapOverlay(),
            ]

        self._play = False
        self._exit = False
        self._add_default_key_functions()
        self._setup_callbacks()

        current_frame = self._get_current_frame()
        self._screen_adjusted_frame_size = calc_screen_adjusted_frame_size(
            screen_size=self._screen_size,
            frame_width=current_frame.shape[1],
            frame_height=current_frame.shape[0],
        )

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
            self._open_player()
            self._input_parser.start()
            self._run_player_loop()
        finally:
            self.__exit__()

    def crop_and_resize_frame(self, frame) -> np.ndarray:
        frame = cv2.resize(frame, self._screen_adjusted_frame_size)
        return frame

    @property
    @abc.abstractmethod
    def _input_parser(self) -> BaseInputParser:
        """
        implemented per platform
        """

    def _run_player_loop(self):
        while not self._exit:
            if self._display_manager.get_in_focus_window_id() != self._window_id:
                self._input_parser.pause()
                if is_window_closed_by_mouse_click(window_name=self._window_name):
                    break
                else:
                    cv2.pollKey()
                    continue
            self._input_parser.resume()
            try:
                single_input = self._input_parser.get_input()
            except Empty:
                cv2.pollKey()
                continue

            self.input_handler.handle_input(single_input)

            if self._play:
                self._play_continuously()
            else:
                frame_for_display = self._create_frame_to_display()
                self._show_frame(frame_for_display)

    def _open_player(self) -> None:
        frame_for_display = self._create_frame_to_display()
        self._show_frame(frame_for_display)
        self._window_id = self._display_manager.get_player_window_id(window_name=self._window_name)
        self._display_manager.set_icon(window_name=self._window_name, window_id=self._window_id)
        cv2.pollKey()

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
                self.input_handler.register_key_function(
                    key_function,
                    callback.__class__.__name__,
                )

            callback.setup(video_player=self, frame=self._get_current_frame())

    def _create_frame_to_display(self) -> np.ndarray:
        original_frame = self._get_current_frame()
        frame_to_display = original_frame.copy()

        for callback in self._frame_edit_callbacks:
            if not callback.enabled:
                continue
            frame_to_display = callback.edit_frame(
                video_player=self,
                frame=frame_to_display,
                frame_num=self._current_frame_num,
                original_frame=original_frame,
            )

        if self._recorder is not None:
            self._recorder.write_frame_to_video(self, frame_to_display, self._current_frame_num)

        return frame_to_display

    def _show_frame(self, frame):
        cv2.imshow(winname=self._window_name, mat=frame)
        cv2.pollKey()

    def _play_continuously(self) -> None:
        while (not self._input_parser.has_input()) and self._play and not self._exit:
            self._change_current_frame_num(change_by=1)
            frame = self._create_frame_to_display()
            self._show_frame(frame)

    def _change_current_frame_num(self, change_by: int) -> None:
        if change_by > 0 and self._current_frame_num == self._last_frame:
            self._play = False
            return

        if change_by < 0 and self._current_frame_num == 0:
            return

        self._current_frame_num = max(0, min(self._current_frame_num + change_by, self._last_frame))

    def _get_current_frame(self) -> np.ndarray:
        return self.frame_reader.get_frame(self._current_frame_num)

    def _pause_and_change_current_frame(self, change_by: int) -> None:
        self._play = False
        self._change_current_frame_num(change_by)

    def _play_pause(self):
        self._play = not self._play

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
        ]

        for key_function in default_key_functions:
            self.input_handler.register_key_function(key_function, "Video Control")



