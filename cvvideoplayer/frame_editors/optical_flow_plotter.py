import numpy as np
import cv2

from . import BaseFrameEditCallback


class OpticalFlowPlotter(BaseFrameEditCallback):

    def __init__(
        self,
        enable_by_default: bool,
        enable_disable_key: str = "o",
        min_arrow_size_to_draw: float = 10.0,
        draw_every_n_arrow: int = 80,
    ):
        super().__init__(enable_by_default, enable_disable_key)
        self._min_arrow_size_to_draw = min_arrow_size_to_draw
        self._draw_every_n_arrow = draw_every_n_arrow

    def edit_frame(
        self,
        video_player: "VideoPlayer",
        frame: np.ndarray,
        original_frame: np.ndarray,
        frame_num: int
    ) -> np.ndarray:

        if frame_num == 0:
            return frame

        prev_frame = video_player.frame_reader.get_frame(frame_num - 1)
        gray_frame, prev_gray_frame = self._convert_frames_to_gray(original_frame, prev_frame)
        flow = self._calc_optical_flow(gray_frame, prev_gray_frame)
        frame = self._create_optical_flow_arrows_image(
            frame=frame,
            optical_flow_image=flow,
        )

        return frame

    def _create_optical_flow_arrows_image(self, optical_flow_image, frame):
        resize_factor = (np.array(frame.shape[:2]) / np.array(optical_flow_image.shape[:2]))

        # Get start and end coordinates of the optical flow
        flow_start = np.stack(np.meshgrid(range(optical_flow_image.shape[1]), range(optical_flow_image.shape[0])), 2)
        flow_end = (flow_start + optical_flow_image[flow_start[:, :, 1], flow_start[:, :, 0]] * 3).astype(np.int32)

        # Threshold values
        norm = np.linalg.norm(flow_end - flow_start, axis=2)
        norm = norm * (norm > self._min_arrow_size_to_draw)

        # Draw all the nonzero values
        nz = np.nonzero(norm)
        for i in range(0, len(nz[0]), self._draw_every_n_arrow):
            y, x = nz[0][i], nz[1][i]
            cv2.arrowedLine(
                frame,
                pt1=tuple((flow_start[y, x] * resize_factor).astype(np.int32)),
                pt2=tuple((flow_end[y, x] * resize_factor).astype(np.int32)),
                color=(0, 255, 0),
                thickness=1,
                tipLength=0.2,
            )

        return frame

    @staticmethod
    def _calc_optical_flow(gray_frame, prev_gray_frame) -> np.ndarray:
        flow = cv2.calcOpticalFlowFarneback(
            prev_gray_frame,
            gray_frame,
            flow=None,
            pyr_scale=0.5,
            levels=5,
            winsize=11,
            iterations=5,
            poly_n=5,
            poly_sigma=1.1,
            flags=0,
        )

        return flow

    @staticmethod
    def _convert_frames_to_gray(frame, prev_frame):
        if len(frame.shape) == 3 and frame.shape[2] == 3:
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            prev_gray_frame = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        else:
            gray_frame = frame
            prev_gray_frame = prev_frame
        return gray_frame, prev_gray_frame
