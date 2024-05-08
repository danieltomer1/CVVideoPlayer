from typing import Dict, Tuple

import numpy as np

from cvvideoplayer.utils.video_player_utils import KeyFunction, write_text_on_img
from ..base_frame_editor import BaseFrameEditor
from ...input_manager import InputManager


class KeyMapOverlay(BaseFrameEditor):
    def __init__(
        self,
        enable_by_default: bool = True,
        video_total_frame_num=None,
        font_scale: float = 1,
        font_thickness: int = 1,
        top_left_coordinate: Tuple[int, int] = (70, 10),
    ):
        super().__init__(enable_by_default)
        self._video_total_frame_num = video_total_frame_num
        self._font_scale = font_scale
        self._font_thickness = font_thickness
        self._tl_coordinate = top_left_coordinate
        self._key_map: Dict[str:KeyFunction] = {}

    @property
    def key_function_to_register(self):
        return [
            KeyFunction(key="ctrl+k", func=self.enable_disable, description="Show/Hide key map"),
        ]

    def setup(self, _) -> None:
        self._key_map = InputManager().clone_keymap()

    def _edit_frame(self, frame: np.ndarray, frame_num: int) -> np.ndarray:
        row = self._tl_coordinate[0]
        for key, key_function in self._key_map.items():
            if not key_function.description:
                continue
            write_text_on_img(
                frame,
                f"{key:20.20}{key_function.description:60.60}",
                row=row,
                col=self._tl_coordinate[1],
                font_scale=self._font_scale,
                thickness=self._font_thickness,
            )
            row += int(20 * self._font_scale)

        return frame

    @property
    def edit_after_resize(self) -> bool:
        return True
