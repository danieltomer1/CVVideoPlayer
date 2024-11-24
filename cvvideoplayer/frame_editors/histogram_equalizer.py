import numpy as np

from .base_frame_edit_callback import BaseFrameEditCallback
from ..utils.video_player_utils import hist_eq, KeyFunction


class HistogramEqualizer(BaseFrameEditCallback):
    def __init__(self, enable_by_default: bool = False):
        super().__init__(enable_by_default)
        self._norm_factor = None

    @property
    def key_function_to_register(self):
        return [
            KeyFunction(
                key="ctrl+h",
                func=self.enable_disable,
                description="Enable/Disable histogram equalization",
            ),
        ]

    def setup(self, frame, **kwargs) -> None:
        if frame.dtype == "uint8":
            self._norm_factor = 2 ** 8 - 1
        elif frame.dtype == "uint16":
            self._norm_factor = 2 ** 16 - 1
        else:
            raise ValueError(f"image must be either Uint8 or Uint16 but got {frame.dtype}")

    def edit_frame(self, frame: np.ndarray, **kwargs) -> np.ndarray:
        frame = hist_eq(frame, self._norm_factor)
        return frame
