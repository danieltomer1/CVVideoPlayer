from typing import Tuple

import numpy as np

from ..base_frame_editor import BaseFrameEditor
from ...utils.video_player_utils import write_text_on_img, KeyFunction


class FrameNumPrinter(BaseFrameEditor):
    def __init__(
        self,
        enable_by_default: bool = True,
        video_total_frame_num=None,
        font_scale: float = 2,
        font_thickness: int = 2,
        bottom_left_coordinate: Tuple[int, int] = (25, 10),
    ):
        super().__init__(enable_by_default)
        self._video_total_frame_num = video_total_frame_num
        self._font_scale = font_scale
        self._font_thickness = font_thickness
        self._bl_coordinate = bottom_left_coordinate
        self._orig_res = None

    @property
    def key_function_to_register(self):
        return [
            KeyFunction(key="ctrl+f", func=self.enable_disable, description="Enable/Disable frame number"),
        ]

    def setup(self, frame) -> None:
        self._orig_res = frame.shape

    def _edit_frame(self, frame: np.ndarray, frame_num: int) -> np.ndarray:
        text = f"{frame_num}"
        if self._video_total_frame_num is not None:
            text += f"/{self._video_total_frame_num - 1}"

        line = write_text_on_img(
            frame,
            text,
            row=self._bl_coordinate[0],
            col=self._bl_coordinate[1],
            font_scale=self._font_scale,
            thickness=self._font_thickness,
        )

        # this should be in a separate frame editor
        write_text_on_img(
            frame,
            f"{self._orig_res[1]}x{self._orig_res[0]}",
            row=line,
            col=self._bl_coordinate[1],
            font_scale=self._font_scale / 1.5,
            thickness=self._font_thickness,
        )
        return frame

    @property
    def edit_after_resize(self) -> bool:
        return True
