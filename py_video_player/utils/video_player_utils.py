import ctypes
import dataclasses
import platform
import subprocess
from ctypes import wintypes
from typing import Callable

import cv2
import numpy as np


@dataclasses.dataclass
class KeymapAction:
    func: Callable
    description: str


def write_text_on_img(img, text, col=10, row=10, font_scale=1.5, color=(255, 255, 255), thickness=2, spacing=30):
    """
    Wrapper for cv2's putText with defaults and meaningful arg names
    """
    cv2.putText(img, text, (col, row), cv2.FONT_HERSHEY_PLAIN, font_scale, color, thickness)
    return row + spacing


def get_forground_window_pid():
    h_wnd = ctypes.windll.user32.GetForegroundWindow()
    pid = ctypes.wintypes.DWORD()
    ctypes.windll.user32.GetWindowThreadProcessId(h_wnd, ctypes.byref(pid))
    return pid.value


def get_keyboard_layout():
    try:
        out = subprocess.check_output("xset -q".split(" ")).decode().strip()
        ind = out.find("LED mask") + 11
        keyboard_layout_code = out[ind : ind + 8]
        if keyboard_layout_code == "00000002":
            return "English"
        elif keyboard_layout_code == "00001002":
            return "Hebrew"
        else:
            raise Exception("unknown keyboard layout")
    except Exception as e:
        return


def hist_eq_uint16(img):
    hist, bins = np.histogram(img.flatten(), 65536, [0, 65536])  # Collect 16 bits histogram (65536 = 2^16).
    cdf = hist.cumsum()

    cdf_m = np.ma.masked_equal(cdf, 0)  # Find the minimum histogram value (excluding 0)
    cdf_m = (cdf_m - cdf_m.min()) * 65535 / (cdf_m.max() - cdf_m.min())
    cdf = np.ma.filled(cdf_m, 0).astype("uint16")

    # Now we have the look-up table...
    hist_eq_img = cdf[img]
    return hist_eq_img


def normalize_image(image, equalize_hist: bool, norm_max=None, norm_min=None):
    if image.dtype == "uint8":
        norm_factor = 255
    elif image.dtype == "uint16":
        norm_factor = 65535
    else:
        raise ValueError(f"image must be either Uint8 or Uint16 but got {image.dtype}")

    image = image.astype("float")
    image /= norm_factor

    if norm_max is not None:
        norm_max = image.max() if norm_max == "img_max" else norm_max / norm_factor
        norm_min = image.min() if norm_min == "img_min" else norm_min / norm_factor
        image = (image - norm_min) / (norm_max - norm_min)
        image = np.clip(image, 0, 1)

    if equalize_hist:
        image = (image * (2**16 - 1)).astype("uint16")
        image = hist_eq_uint16(image) / (2**16 - 1)

    image = (image * 255).astype("uint8")
    return image


def get_screen_size():
    if platform.system() == "Linux":
        return get_screen_size_linux()
    elif platform.system() == "Windows":
        return get_screen_size_windows()


def get_screen_size_linux():
    try:
        screen_size_str = (
            subprocess.check_output('xrandr | grep "\*" | cut -d" " -f4', shell=True).decode().strip().split("\n")[0]
        )
        screen_w, screen_h = screen_size_str.split("x")
        screen_w = 0.9 * int(screen_w)
        screen_h = 0.9 * int(screen_h)
        return screen_w, screen_h
    except (ValueError, TypeError, subprocess.CalledProcessError, IndexError):
        return None, None


def get_screen_size_windows():
    user32 = ctypes.windll.user32
    screensize = 0.9 * user32.GetSystemMetrics(0), 0.9 * user32.GetSystemMetrics(1)
    return screensize


def get_screen_adjusted_frame_size(screen_size, frame_width, frame_height):
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
