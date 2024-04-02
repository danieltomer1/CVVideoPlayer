import abc
import random
from pathlib import Path
import mimetypes
from typing import Optional

import cv2
import numpy as np
from decord import VideoReader, cpu

RANDOM_STATE = random.Random(42)


class FrameReader(abc.ABC):
    @abc.abstractmethod
    def get_frame(self, frame_num: int) -> Optional[np.ndarray]:
        pass

    @abc.abstractmethod
    def __len__(self) -> int:
        pass


class LocalFrameReader(FrameReader):
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
        self._video_reader = VideoReader(str(self._video_path), ctx=cpu(0))

    def get_frame(self, frame_num):
        if frame_num >= len(self):
            return
        img = self._video_reader[frame_num].asnumpy()
        if img.shape[-1] == 3:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        assert img is not None, f"no image found in {self._video_reader[frame_num]}"
        return img

    def __len__(self):
        return len(self._video_reader)


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


def extract_digits_from_str(string):
    return "".join([char for char in string if char.isdigit()])
