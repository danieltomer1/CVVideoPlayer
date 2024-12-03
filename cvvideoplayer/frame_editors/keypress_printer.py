import time
from typing import Tuple, TYPE_CHECKING

import cv2
import numpy as np

from .base_frame_edit_callback import BaseFrameEditCallback
from ..utils.ui_utils import InputType
from ..utils.video_player_utils import KeyFunction
from ..utils.drawing_utils import write_text_on_img

if TYPE_CHECKING:
    from ..video_players.base_video_player import VideoPlayer


class KeypressPrinter(BaseFrameEditCallback):
    def __init__(
        self,
        enable_by_default: bool = True,
        font_scale: float = 2,
        font_thickness: int = 3,
        top_left_coordinate: Tuple[int, int] = (0.4, 0.1),
    ):
        super().__init__(enable_by_default)
        self._font_scale = font_scale
        self._font_thickness = font_thickness
        self._tl_coordinate = top_left_coordinate

    @property
    def key_function_to_register(self):
        return [
            KeyFunction(key="ctrl+p", func=self.enable_disable, description="Show/Hide frame info"),
        ]

    def edit_frame(
            self,
            video_player: "VideoPlayer",
            frame: np.ndarray,
            frame_num: int,
            original_frame: np.ndarray,
    ) -> np.ndarray:
        last_input, press_time = video_player.last_key_press_event
        if last_input is None:
            return frame

        time_diff = time.time() - press_time
        if time_diff > 0.5:
            return frame

        if last_input.input_type == InputType.KeyPress:
            text = f"Key pressed: {last_input.input_data}"
            overlay = frame.copy()
            write_text_on_img(
                overlay,
                text,
                row=int(self._tl_coordinate[1] * frame.shape[0]),
                col=int(self._tl_coordinate[0] * frame.shape[1]),
                font_scale=self._font_scale,
                thickness=self._font_thickness,
                color=(255, 0, 0)
            )

            alpha = 1 - time_diff * 2
            frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

        return frame
