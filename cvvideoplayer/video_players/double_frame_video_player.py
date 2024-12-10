import time
from copy import deepcopy
from functools import partial
from pathlib import Path
from typing import Union, Optional, List

import cv2
import numpy as np

from .base_video_player import VideoPlayer
from ..display_managers.abstract_display_manager import DisplayManager
from ..input_management.base_input_parser import BaseInputParser
from ..utils.drawing_utils import draw_rectangle
from ..utils.video_player_utils import KeyFunction, WindowStatus
from ..frame_reader import FrameReader
from ..recorder import AbstractRecorder
from ..frame_editors import BaseFrameEditCallback
from ..input_management.input_handler import InputHandler
from ..utils.video_player_utils import calc_screen_adjusted_frame_size


class DoubleFrameVideoPlayer(VideoPlayer):
    def __init__(
        self,
        video_source: Union[str, Path, FrameReader],
        display_manager: DisplayManager,
        input_parser: BaseInputParser,
        start_from_frame: int = 0,
        left_frame_callbacks: Optional[List[BaseFrameEditCallback]] = None,
        right_frame_callbacks: Optional[List[BaseFrameEditCallback]] = None,
        record: Union[bool, AbstractRecorder] = False,
    ):
        super().__init__(
            video_source=video_source,
            start_from_frame=start_from_frame,
            frame_edit_callbacks=left_frame_callbacks,
            record=record,
            display_manager=display_manager,
            input_parser=input_parser,
        )

        self.second_input_handler = InputHandler(self._window_name)

        self._current_side = "right"
        self._border_size = 10

        if right_frame_callbacks is None:
            self._right_frame_callbacks = deepcopy(left_frame_callbacks)
        else:
            self._right_frame_callbacks = right_frame_callbacks

        self._add_more_video_control_key_functions()
        self._setup_right_screen_callbacks()

    def _setup_right_screen_callbacks(self):
        for callback in self._right_frame_callbacks:
            for key_function in callback.key_function_to_register:
                self.second_input_handler.register_key_function(
                    key_function,
                    callback.__class__.__name__,
                )

            callback.setup(video_player=self, frame=self._get_current_frame())

    def _add_more_video_control_key_functions(self) -> None:
        for key_function in self.video_control_key_functions:
            self.second_input_handler.register_key_function(key_function, "Video Control")

        additional_key_functions = [
            KeyFunction("ctrl+1", partial(self._set_current_side, "left"), "set focus to left frame"),
            KeyFunction("ctrl+2", partial(self._set_current_side, "right"), "set focus to right frame"),
        ]

        for key_function in additional_key_functions:
            self.input_handler.register_key_function(key_function, "Video Control")
            self.second_input_handler.register_key_function(key_function, "Video Control")

    def _set_current_side(self, side):
        self._current_side = side

    def _run_player_loop(self):
        while not self._exit:
            window_status = self._get_window_status()
            if window_status == WindowStatus.closed:
                break
            elif window_status == WindowStatus.out_of_focus:
                self._input_parser.pause()
                cv2.pollKey()
                continue
            else:
                self._input_parser.resume()
                single_input = self._get_user_input()
                if single_input is None:
                    continue

            if self._current_side == "left":
                self.input_handler.handle_input(single_input)
            elif self._current_side == "right":
                self.second_input_handler.handle_input(single_input)

            if self._play:
                self._play_continuously()
            else:
                self._show_current_frame()

    def _create_frame_to_display(self, original_frame, record_frame) -> np.ndarray:
        frame_1_to_display = super()._create_frame_to_display(original_frame=original_frame, record_frame=False)
        frame_2_to_display = original_frame.copy()

        for callback in self._right_frame_callbacks:
            if not callback.enabled:
                continue
            frame_2_to_display = callback.edit_frame(
                video_player=self,
                frame=frame_2_to_display,
                frame_num=self._current_frame_num,
                original_frame=original_frame,
            )

        double_frame = np.hstack(
            (
                frame_1_to_display,
                np.zeros((frame_1_to_display.shape[0], self._border_size, 3), dtype=np.uint8),
                frame_2_to_display,
            )
        )

        if record_frame and self._recorder is not None:
            self._recorder.write_frame_to_video(self, double_frame, self._current_frame_num)

        draw_rectangle(
            double_frame,
            x=0 if self._current_side == "left" else frame_1_to_display.shape[1] + self._border_size,
            y=0,
            w=frame_1_to_display.shape[1],
            h=frame_1_to_display.shape[0],
            color=(0, 255, 0),
            thickness=3,
            only_corners=False
        )

        screen_adjusted_frame_size = calc_screen_adjusted_frame_size(
            screen_size=self._screen_size,
            frame_width=double_frame.shape[1],
            frame_height=double_frame.shape[0],
        )

        double_frame = cv2.resize(double_frame, screen_adjusted_frame_size)

        return double_frame
