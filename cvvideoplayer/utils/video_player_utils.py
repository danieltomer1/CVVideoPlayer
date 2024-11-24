import dataclasses
from enum import Enum
from pathlib import Path
import platform
from typing import Callable

import cv2
import numpy as np
from ..frame_reader import LocalVideoFileReader, LocalDirReader, FrameReader
from ..recorder import AbstractRecorder, SimpleRecorder


class SupportedOS(Enum):
    LINUX = "Linux"
    WINDOWS = "Windows"


CURRENT_OS = SupportedOS(platform.system())


@dataclasses.dataclass
class KeyFunction:
    key: str
    func: Callable
    description: str


def get_frame_reader(video_source):
    if isinstance(video_source, (str, Path)):
        path = Path(video_source)
        if path.is_file():
            frame_reader = LocalVideoFileReader(video_source)
        elif path.is_dir():
            frame_reader = LocalDirReader
        else:
            raise IOError(f"{video_source} not found")
    elif isinstance(video_source, FrameReader):
        frame_reader = video_source
    else:
        raise ValueError(
            "video_source can needs to be one of {path to a video file, path to frame folder,"
            " an object of a class that implements FrameReader}"
        )
    return frame_reader


def get_recorder(record):
    if isinstance(record, AbstractRecorder):
        recorder = record
    elif isinstance(record, bool):
        recorder = SimpleRecorder() if record else None
    else:
        raise ValueError(
            "record can needs to be one of {True, False," " an object of a class that implements AbstractRecorder}"
        )
    return recorder


def hist_eq(img, max_value):
    hist, bins = np.histogram(img.flatten(), max_value, (0, max_value))  # Collect 16 bits histogram (65536 = 2^16).
    cdf = hist.cumsum()

    cdf_m = np.ma.masked_equal(cdf, 0)  # Find the minimum histogram value (excluding 0)
    cdf_m = (cdf_m - cdf_m.min()) * max_value / (cdf_m.max() - cdf_m.min())
    if max_value == 255:
        cdf = np.ma.filled(cdf_m, 0,).astype("uint8")
    else:
        cdf = np.ma.filled(cdf_m, 0).astype("uint16")

    # Now we have the look-up table...
    hist_eq_img = cdf[img]
    return hist_eq_img


def calc_screen_adjusted_frame_size(screen_size, frame_width, frame_height):
    screen_w, screen_h = screen_size
    if screen_w is None:
        return frame_width, frame_height

    adjusted_w = screen_w
    adjusted_h = screen_h
    if screen_w != frame_width:
        w_ratio = screen_w / frame_width
        adjusted_w = screen_w
        adjusted_h = frame_height * w_ratio
    if screen_h < adjusted_h:
        h_ratio = screen_h / adjusted_h
        adjusted_h = screen_h
        adjusted_w *= h_ratio

    return int(adjusted_w), int(adjusted_h)


def is_window_closed_by_mouse_click(window_name):
    return cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1
