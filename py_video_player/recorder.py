from pathlib import Path
from typing import Tuple

import cv2


class Recorder:
    def __init__(
        self,
        output_video_path: Path,
        recorded_video_fps: int,
        output_video_shape: Tuple[int, int],
    ):

        self._output_video_path = output_video_path
        self._recorded_video_fps = recorded_video_fps
        self._output_video_shape = output_video_shape
        self._video_writer = self._create_video_writer()

    def _create_video_writer(self):
        if self._output_video_path is None:
            return
        print(f"Saving video in {self._output_video_path}")
        self._output_video_path.parent.mkdir(exist_ok=True, parents=True)
        fourcc = cv2.VideoWriter_fourcc("m", "p", "4", "v")
        video_writer = cv2.VideoWriter(
            str(self._output_video_path),
            fourcc,
            self._recorded_video_fps,
            self._output_video_shape,
        )
        return video_writer

    def write_frame_to_video(self, frame):
        frame = cv2.resize(frame, self._output_video_shape)
        self._video_writer.write(frame)

    def teardown(self):
        self._video_writer.release()
