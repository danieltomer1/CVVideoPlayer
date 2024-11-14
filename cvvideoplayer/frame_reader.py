import abc
import random
from pathlib import Path
import mimetypes
from typing import Optional

import cv2
import numpy as np

RANDOM_STATE = random.Random(42)


class FrameReader(abc.ABC):
    """
    The frame reader is used in the video player to fetch frames according to a frame number
    """

    @abc.abstractmethod
    def get_frame(self, frame_num: int) -> Optional[np.ndarray]:
        pass

    @abc.abstractmethod
    def __len__(self) -> int:
        pass


class LocalFrameReader(FrameReader):
    """
    A frame reader used to read any local video file or folder containing the frames as images
    (as long as there is a number in the name of the image files indicating their order).
    """

    def __init__(self, source_path):
        """
        Args:
            source_path: can be either a local video file path or a path to a directory containing frames as single
            images. the images need to contain a integer in their name specifying the frame order.
        """
        if Path(source_path).is_dir():
            self._reader = LocalDirReader(source_path)
        elif mimetypes.guess_type(source_path)[0].startswith("video"):
            self._reader = LocalVideoFileReader(source_path)
        else:
            raise NotImplementedError(f"{source_path=} is not a video file or directory")

    def get_frame(self, frame_num: int):
        return self._reader.get_frame(frame_num)

    def __len__(self):
        return len(self._reader)


class LocalVideoFileReader(FrameReader):
    def __init__(self, local_video_path: str):
        self._video_path = Path(local_video_path)
        assert self._video_path.is_file()
        self._video_reader = cv2.VideoCapture(str(self._video_path))
        self._total_frames = int(self._video_reader.get(cv2.CAP_PROP_FRAME_COUNT))
        self._last_frame = -1

    def get_frame(self, frame_num):
        if frame_num >= len(self):
            return
        if not frame_num == self._last_frame + 1:
            self._video_reader.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret, frame = self._video_reader.read()
        assert ret, f"frame number = {frame_num} is corrupted"
        self._last_frame = frame_num
        return frame

    def __len__(self):
        return self._total_frames


class LocalDirReader(FrameReader):
    def __init__(self, local_frame_dir):
        self.local_frame_dir = local_frame_dir
        self._frame_paths = self._create_frame_list()

    def _create_frame_list(self):
        self._frame_paths = list(Path(self.local_frame_dir).glob("*"))
        self._frame_paths = [path for path in self._frame_paths if mimetypes.guess_type(path)[0].startswith("image")]

        if len(self._frame_paths) == 0:
            raise (Exception(f"No image files found in dir {self.local_frame_dir}"))

        self._frame_paths = sorted(self._frame_paths, key=lambda x: int(extract_digits_from_str(x.stem)))
        return self._frame_paths

    def get_frame(self, frame_num):
        if frame_num >= len(self):
            return
        img = cv2.imread(str(self._frame_paths[frame_num]), -1)
        assert img is not None, f"no image found in {self._frame_paths[frame_num]}"
        return img

    def __len__(self):
        return len(self._frame_paths)


class TestingFrameReader(FrameReader):
    def __init__(self, video_len=20):
        self._video = np.random.randint(low=0, high=255, size=(video_len, 10, 10, 3), dtype=np.uint8)

    def get_frame(self, frame_num: int) -> Optional[np.ndarray]:
        if frame_num >= len(self):
            return
        return self._video[frame_num]

    def __len__(self) -> int:
        return self._video.shape[0]


def extract_digits_from_str(string):
    return "".join([char for char in string if char.isdigit()])
