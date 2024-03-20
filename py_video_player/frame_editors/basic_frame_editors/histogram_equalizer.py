import numpy as np

from ..base_frame_editor import BaseFrameEditor
from ...utils.video_player_utils import hist_eq_uint16


class HistogramEqualizer(BaseFrameEditor):
    def __init__(self, enable_by_default: bool = False):
        super().__init__(enable_by_default)

    def _edit_frame(self, frame: np.ndarray, frame_num: int) -> np.ndarray:
        if frame.dtype == "uint8":
            norm_factor = 255
        elif frame.dtype == "uint16":
            norm_factor = 65535
        else:
            raise ValueError(f"image must be either Uint8 or Uint16 but got {frame.dtype}")

        frame = frame.astype("float")
        frame /= norm_factor

        frame = (frame * (2**16 - 1)).astype("uint16")
        frame = (hist_eq_uint16(frame) / 255).astype("uint8")
        return frame

    @property
    def edit_after_resize(self) -> bool:
        return False
