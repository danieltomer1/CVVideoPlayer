import numpy as np
from .base_frame_edit_callback import BaseFrameEditCallback


class FitFrameToScreen(BaseFrameEditCallback):
    def __init__(
        self,
        enable_by_default: bool = True,
    ):
        super().__init__(enable_by_default)

    def edit_frame(self, video_player, frame: np.ndarray, **kwargs) -> np.ndarray:
        frame = video_player.crop_and_resize_frame(frame)
        return frame
