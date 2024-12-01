import cv2
import numpy as np

from .double_frame_video_player import DoubleFrameVideoPlayer
from ..utils.video_player_utils import KeyFunction
from ..input_management.windows_input_parser import WindowsInputParser
from .base_video_player import VideoPlayer


class WindowsVideoPlayer(VideoPlayer):
    def __init__(self, **video_player_kwargs):
        super().__init__(**video_player_kwargs)
        self._zoom_factor = 1.0
        self._zoom_crop_xywh = None
        current_frame = self._get_current_frame()
        self._original_frame_size = tuple(current_frame.shape[:2][::-1])
        self._zoom_crop_xywh = (
            0,
            0,
            self._original_frame_size[0],
            self._original_frame_size[1],
        )

    def _show_frame(self, frame) -> None:
        super()._show_frame(frame)
        cv2.pollKey()  # for some reason Windows OS requires an additional waitKey to work properly

    @property
    def _input_parser(self):
        return WindowsInputParser()

    def _add_default_key_functions(self) -> None:
        super()._add_default_key_functions()
        scroll_to_zoom = KeyFunction(key="mouse_scroll", func=self._set_zoom, description="zoom in and out")
        self.input_handler.register_key_function(key_function=scroll_to_zoom, callback_name="Video Control")

    def _set_zoom(self, curser_x: int, curser_y: int, scroll_direction: int):
        new_zoom_factor = max(1.0, min(5.0, self._zoom_factor + 0.5 * scroll_direction))
        if new_zoom_factor != self._zoom_factor:
            self._zoom_factor = new_zoom_factor
            adjusted_width, adjusted_height = self._screen_adjusted_frame_size
            norm_curser_position = (
                curser_x / adjusted_width,
                curser_y / adjusted_height,
            )
            w = h = 1 / self._zoom_factor
            x_min = norm_curser_position[0] * (1 - w)
            y_min = norm_curser_position[1] * (1 - h)
            self._zoom_crop_xywh = (
                int(self._original_frame_size[0] * x_min),
                int(self._original_frame_size[1] * y_min),
                int(self._original_frame_size[0] * w),
                int(self._original_frame_size[1] * h),
            )

    def crop_and_resize_frame(self, frame) -> np.ndarray:
        frame = frame[
            self._zoom_crop_xywh[1] : self._zoom_crop_xywh[1] + self._zoom_crop_xywh[3],
            self._zoom_crop_xywh[0] : self._zoom_crop_xywh[0] + self._zoom_crop_xywh[2],
        ]
        frame = cv2.resize(frame, self._screen_adjusted_frame_size)
        return frame


class WindowsDoubleFrameVideoPlayer(DoubleFrameVideoPlayer, WindowsVideoPlayer):
    def _show_frame(self, frame) -> None:
        super()._show_frame(frame)
        cv2.pollKey()  # for some reason Windows OS requires an additional waitKey to work properly

    @property
    def _input_parser(self):
        return WindowsInputParser()
