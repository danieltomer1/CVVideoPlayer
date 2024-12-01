from abc import ABC
from copy import deepcopy
from functools import partial
from pathlib import Path
from queue import Empty
from typing import Union, Optional, List

import cv2
import numpy as np

from .base_video_player import VideoPlayer
from ..display_managers.abstract_display_manager import DisplayManager
from ..utils.video_player_utils import KeyFunction
from ..frame_reader import FrameReader
from ..recorder import AbstractRecorder
from ..frame_editors import BaseFrameEditCallback
from ..input_management.input_handler import InputHandler
from ..utils.video_player_utils import is_window_closed_by_mouse_click, calc_screen_adjusted_frame_size


class DoubleFrameVideoPlayer(VideoPlayer, ABC):
    def __init__(
            self,
            video_source: Union[str, Path, FrameReader],
            display_manager: DisplayManager,
            start_from_frame: int = 0,
            frame_edit_callbacks: Optional[List[BaseFrameEditCallback]] = None,
            record: Union[bool, AbstractRecorder] = False,
    ):
        self._window_name = "CVvideoPlayer"
        self._display_manager = display_manager
        self._current_side = "left"
        self._second_screen_callbacks = deepcopy(frame_edit_callbacks)
        self._second_input_handler = InputHandler(self._window_name)
        self._border_size = 10
        super().__init__(
            video_source=video_source,
            start_from_frame=start_from_frame,
            frame_edit_callbacks=frame_edit_callbacks,
            record=record,
            display_manager=display_manager
        )

    def _setup_callbacks(self):
        super()._setup_callbacks()
        for callback in self._second_screen_callbacks:
            for key_function in callback.key_function_to_register:
                self._second_input_handler.register_key_function(
                    key_function,
                    callback.__class__.__name__,
                )

            callback.setup(video_player=self, frame=self._get_current_frame())

    def _add_default_key_functions(self) -> None:
        super()._add_default_key_functions()
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
            self._second_input_handler.register_key_function(key_function, "Video Control")

        additional_key_functions = [
            KeyFunction("ctrl+1", partial(self._set_current_side, "left"), "set focus to left frame"),
            KeyFunction("ctrl+2", partial(self._set_current_side, "right"), "set focus to right frame"),
        ]

        for key_function in additional_key_functions:
            self.input_handler.register_key_function(key_function, "Video Control")
            self._second_input_handler.register_key_function(key_function, "Video Control")

    def _set_current_side(self, side):
        self._current_side = side

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

            if self._current_side == "left":
                self.input_handler.handle_input(single_input)
            elif self._current_side == "right":
                self._second_input_handler.handle_input(single_input)

            if self._play:
                self._play_continuously()
            else:
                frame_for_display = self._create_frame_to_display()
                self._show_frame(frame_for_display)

    def _create_frame_to_display(self) -> np.ndarray:
        original_frame = self._get_current_frame()
        frame_1_to_display = super()._create_frame_to_display()
        frame_2_to_display = original_frame.copy()

        for callback in self._second_screen_callbacks:
            if not callback.enabled:
                continue
            frame_2_to_display = callback.edit_frame(
                video_player=self,
                frame=frame_2_to_display,
                frame_num=self._current_frame_num,
                original_frame=original_frame,
            )

        double_frame = np.hstack((
            frame_1_to_display,
            np.zeros((frame_1_to_display.shape[0], self._border_size, 3), dtype=np.uint8),
            frame_2_to_display
        ))

        screen_adjusted_frame_size = calc_screen_adjusted_frame_size(
            screen_size=self._screen_size,
            frame_width=double_frame.shape[1],
            frame_height=double_frame.shape[0],
        )

        double_frame = cv2.resize(double_frame, screen_adjusted_frame_size)

        if self._recorder is not None:
            self._recorder.write_frame_to_video(self, double_frame, self._current_frame_num)

        return double_frame
