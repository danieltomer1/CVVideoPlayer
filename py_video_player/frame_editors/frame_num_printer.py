from typing import Tuple

import numpy as np

from .base_frame_editor import BaseFrameEditor
from ..utils.video_player_utils import write_text_on_img


class FrameNumPrinter(BaseFrameEditor):
    def __init__(
        self,
        enable_by_default: bool = True,
        font_scale: float = 2,
        font_thickness: int = 2,
        tl_coordinate: Tuple[int, int] = (25, 10)
    ):
        super().__init__(enable_by_default)
        self._font_scale = font_scale
        self._font_thickness = font_thickness
        self._tl_coordinate = tl_coordinate

    def _edit_frame(self, frame: np.ndarray, frame_num: int) -> np.ndarray:
        write_text_on_img(
            frame,
            f"{frame_num}",
            row=self._tl_coordinate[0],
            col=self._tl_coordinate[1],
            font_scale=self._font_scale,
            thickness=self._font_thickness,
        )
        return frame

    def edit_after_resize(self) -> bool:
        return True
