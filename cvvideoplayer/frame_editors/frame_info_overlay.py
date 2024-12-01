from typing import Tuple

import numpy as np

from .base_frame_edit_callback import BaseFrameEditCallback
from ..utils.drawing_utils import write_text_on_img


class FrameInfoOverlay(BaseFrameEditCallback):
    def __init__(
        self,
        enable_by_default: bool = True,
        enable_disable_key: str = "ctrl+f",
        font_scale: float = 2,
        font_thickness: int = 2,
        top_left_coordinate: Tuple[int, int] = (10, 10),
    ):
        super().__init__(enable_by_default, enable_disable_key)
        self._font_scale = font_scale
        self._font_thickness = font_thickness
        self._tl_coordinate = top_left_coordinate

    def edit_frame(
            self,
            video_player,
            frame: np.ndarray,
            frame_num: int,
            original_frame: np.ndarray,
    ) -> np.ndarray:

        text = f"{frame_num}"
        if len(video_player.frame_reader) is not None:
            text += f"/{len(video_player.frame_reader) - 1}"

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
            f"{original_frame.shape[1]}x{original_frame.shape[0]}",
            row=line,
            col=self._tl_coordinate[1],
            font_scale=self._font_scale / 1.5,
            thickness=self._font_thickness,
        )
        return frame
