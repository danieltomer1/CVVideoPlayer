import numpy as np

from .base_frame_edit_callback import BaseFrameEditCallback
from ..utils.video_player_utils import hist_eq, KeyFunction


class HistogramEqualizer(BaseFrameEditCallback):
    def __init__(
            self,
            enable_by_default: bool = False,
            enable_disable_key: str = "ctrl+h"
    ):
        super().__init__(enable_by_default, enable_disable_key)

    def edit_frame(self, frame: np.ndarray, **kwargs) -> np.ndarray:
        if frame.dtype == "uint8":
            norm_factor = 2 ** 8 - 1
        elif frame.dtype == "uint16":
            norm_factor = 2 ** 16 - 1
        else:
            raise ValueError(f"image must be either Uint8 or Uint16 but got {frame.dtype}")

        frame = hist_eq(frame, norm_factor)
        return frame
