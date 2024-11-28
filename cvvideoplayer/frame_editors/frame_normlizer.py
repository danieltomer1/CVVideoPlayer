from typing import Union

import numpy as np

from .base_frame_edit_callback import BaseFrameEditCallback
from ..utils.video_player_utils import KeyFunction


class FrameNormalizer(BaseFrameEditCallback):
    def __init__(
        self,
        enable_by_default: bool = True,
        range_min: Union[str, int] = "",
        range_max: Union[str, int] = "",
    ):
        super().__init__(enable_by_default)
        self._range_min = range_min
        self._range_max = range_max

    @property
    def key_function_to_register(self):
        return [
            KeyFunction(key="r", func=self._set_dynamic_range, description="Set dynamic range"),
        ]

    def edit_frame(self, frame, **kwargs) -> np.ndarray:
        if frame.dtype == "uint8":
            norm_factor = 2 ** 8 - 1
        elif frame.dtype == "uint16":
            norm_factor = 2 ** 16 - 1
        else:
            raise ValueError(f"image must be either Uint8 or Uint16 but got {frame.dtype}")

        frame = frame.astype("float")
        frame /= norm_factor

        if self._range_min or self._range_max:
            norm_min = int(self._range_min) / norm_factor if self._range_min else 0
            norm_max = int(self._range_max) / norm_factor if self._range_max else norm_factor
            frame = (frame - norm_min) / (norm_max - norm_min)
            frame = np.clip(frame, 0, 1)

        frame = (frame * 255).astype("uint8")
        return frame

    def _set_dynamic_range(self):
        self._range_min = input("Set new image min: ")
        self._range_max = input("Set new image max: ")
