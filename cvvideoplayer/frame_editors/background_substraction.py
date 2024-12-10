import numpy as np
import cv2

from . import BaseFrameEditCallback


class BackgroundSub(BaseFrameEditCallback):

    def __init__(
        self,
        enable_by_default: bool,
        enable_disable_key: str = "b",
    ):
        super().__init__(enable_by_default, enable_disable_key)
        self._back_sub = None
        self._prev_frame_num = -1
        self._fg_mask = None

    def setup(self, video_player: "VideoPlayer", frame) -> None:
        self._back_sub = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=50, detectShadows=True)

    def edit_frame(
        self,
        video_player: "VideoPlayer",
        frame: np.ndarray,
        original_frame: np.ndarray,
        frame_num: int,
    ) -> np.ndarray:

        if frame_num == self._prev_frame_num:
            return self._fg_mask

        gray_frame = self._convert_to_gray(original_frame)
        fg_mask = self._back_sub.apply(gray_frame)
        fg_mask = cv2.resize(fg_mask, (frame.shape[1], frame.shape[0]))

        self._fg_mask = np.dstack([fg_mask] * 3)
        self._prev_frame_num = frame_num

        return self._fg_mask

    @staticmethod
    def _convert_to_gray(frame):
        if len(frame.shape) == 3 and frame.shape[2] == 3:
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            gray_frame = frame
        return gray_frame
