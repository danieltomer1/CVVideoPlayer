from pathlib import Path
import cv2
import numpy as np
from .base_frame_edit_callback import BaseFrameEditCallback

from typing import Tuple


class FrameSnapshot(BaseFrameEditCallback):
    """
    In charge of saving a specific frame to a file
    """

    def __init__(self, output_video_path: Path, output_shape: Tuple[int, int], frame_num: int):
        super().__init__(enable_by_default=True)
        self._output_video_path = output_video_path
        self._output_shape = output_shape
        self._frame_num = frame_num

    def edit_frame(self, frame: np.ndarray, frame_num: int, **kwargs):
        if frame_num == self._frame_num:
            cv2.imwrite(str(self._output_video_path), cv2.resize(frame, self._output_shape))
            print(f"Saved frame {frame_num} to {self._output_video_path}")

            # TODO: This is a hack to make sure we only save the frame once, but it's not a good solution
            self._enabled = False  # For some reason, we get here twice, so we need to disable it after the first time
        return frame
