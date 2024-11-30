from typing import Tuple

import numpy as np

from ..utils.drawing_utils import write_text_on_img
from .base_frame_edit_callback import BaseFrameEditCallback


class KeyMapOverlay(BaseFrameEditCallback):
    def __init__(
        self,
        enable_by_default: bool = True,
        enable_disable_key: str = "ctrl+k",
        font_scale: float = 1,
        font_thickness: int = 1,
        font_color: Tuple[int, int, int] = (255, 255, 125),
        top_left_coordinate: Tuple[int, int] = (90, 10),
    ):
        super().__init__(enable_by_default, enable_disable_key)
        self._font_scale = font_scale
        self._font_thickness = font_thickness
        self._font_color = font_color
        self._tl_coordinate = top_left_coordinate

    def edit_frame(self, video_player, frame: np.ndarray, frame_num: int, **kwargs) -> np.ndarray:
        row = self._tl_coordinate[0]
        write_text_on_img(
            frame,
            "Available keyboard shortcuts (hide with ctrl+k):",
            row=row,
            col=self._tl_coordinate[1],
            font_scale=self._font_scale * 1.2,
            thickness=self._font_thickness + 1,
            color=self._font_color,
        )
        row += int(30 * self._font_scale)
        for callback_name, keys in video_player.input_handler.get_keymap_description().items():
            write_text_on_img(
                frame,
                f"{callback_name}:",
                row=row,
                col=self._tl_coordinate[1],
                font_scale=self._font_scale,
                thickness=self._font_thickness + 1,
                color=self._font_color,
            )
            row += int(20 * self._font_scale)
            for key, desc in keys:
                write_text_on_img(
                    frame,
                    key,
                    row=row,
                    col=self._tl_coordinate[1],
                    font_scale=self._font_scale,
                    thickness=self._font_thickness,
                    color=self._font_color,
                )
                write_text_on_img(
                    frame,
                    f": {desc}",
                    row=row,
                    col=self._tl_coordinate[1] + 150,
                    font_scale=self._font_scale,
                    thickness=self._font_thickness,
                    color=self._font_color,
                )
                row += int(20 * self._font_scale)
            row += int(10 * self._font_scale)
        return frame
