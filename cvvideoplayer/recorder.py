from abc import ABC, abstractmethod
from pathlib import Path
from typing import Tuple, TYPE_CHECKING

import cv2
import numpy as np

if TYPE_CHECKING:
    from .video_players.base_video_player import VideoPlayer


class AbstractRecorder(ABC):

    @abstractmethod
    def write_frame_to_video(self, video_player: "VideoPlayer", frame: np.ndarray, frame_nun: int) -> None:
        """
        method that receives a frame and writes in to a file
        """

    @abstractmethod
    def teardown(self) -> None:
        """
        what to do on closing of the player
        """


class SimpleRecorder(AbstractRecorder):
    """
    In charge of recording what ever the video player is playing. The output video will be saved in
    output_video_path
    """

    def __init__(
        self,
        output_video_path: Path = Path("./outputs/recorded_video.mp4"),
        recorded_video_fps: int = 30,
        output_video_shape: Tuple[int, int] = (640, 512),
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

    def write_frame_to_video(self, video_player, frame, frame_num):
        frame = cv2.resize(frame, self._output_video_shape)
        self._video_writer.write(frame)

    def teardown(self):
        self._video_writer.release()
