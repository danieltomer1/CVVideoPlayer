from typing import Tuple

import numpy as np

from ..base_frame_edit_callback import BaseFrameEditCallback
from ...utils.video_player_utils import KeyFunction
from ...utils.drawing_utils import write_text_on_img


class FrameInfoOverlay(BaseFrameEditCallback):
    def __init__(
        self,
        enable_by_default: bool = True,
        font_scale: float = 2,
        font_thickness: int = 2,
        top_left_coordinate: Tuple[int, int] = (10, 10),
    ):
        super().__init__(enable_by_default)
        self._video_total_frame_num = None
        self._font_scale = font_scale
        self._font_thickness = font_thickness
        self._tl_coordinate = top_left_coordinate
        self._orig_res = None

    @property
    def key_function_to_register(self):
        return [
            KeyFunction(key="ctrl+f", func=self.enable_disable, description="Show/Hide frame info"),
        ]

    def setup(self, video_player, frame) -> None:
        self._video_total_frame_num = len(video_player.frame_reader)
        self._orig_res = frame.shape

    def after_frame_resize(self, video_player, frame: np.ndarray, frame_num: int) -> np.ndarray:
        text = f"{frame_num}"
        if self._video_total_frame_num is not None:
            text += f"/{self._video_total_frame_num - 1}"

        line = write_text_on_img(
            frame,
            text,
            row=self._tl_coordinate[0],
            col=self._tl_coordinate[1],
            font_scale=self._font_scale,
            thickness=self._font_thickness,
        )

        write_text_on_img(
            frame,
            f"{self._orig_res[1]}x{self._orig_res[0]}",
            row=line,
            col=self._tl_coordinate[1],
            font_scale=self._font_scale / 1.5,
            thickness=self._font_thickness,
        )
        return frame
