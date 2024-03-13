import random
from pathlib import Path
from typing import Optional

import cv2
import abc

import numpy as np
from decord import VideoReader, cpu

RANDOM_STATE = random.Random(42)


class AbstractImageReader(abc.ABC):
    @abc.abstractmethod
    def get_frame(self, frame_num: int) -> Optional[np.ndarray]:
        pass

    @abc.abstractmethod
    def __len__(self) -> int:
        pass


class ImageReader(AbstractImageReader):
    def __init__(self, data_source_name, data_source_path):
        if data_source_name == "local_video_path":
            self._reader = VideoFileReader(data_source_path)
        elif data_source_name == "local_frame_dir":
            self._reader = LocalDirImageReader(data_source_path)
        else:
            raise NotImplementedError(f"{data_source_name=} is not one of the supported data sources")

    def get_frame(self, frame_num: int):
        return self._reader.get_frame(frame_num)

    def __len__(self):
        return len(self._reader)


class VideoFileReader(AbstractImageReader):
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


class LocalDirImageReader(AbstractImageReader):
    def __init__(self, local_frame_dir):
        self.local_frame_dir = local_frame_dir
        self._extensions = [".tif", ".png", ".tiff", ".JPEG", ".jpg"]
        self._frame_paths = self._create_frame_list()

    def _create_frame_list(self):
        self._frame_paths = list(Path(self.local_frame_dir).glob("*"))
        self._frame_paths = [path for path in self._frame_paths if path.suffix in self._extensions]

        if len(self._frame_paths) == 0:
            raise (Exception(f"No files found in dir {self.local_frame_dir}"))

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
