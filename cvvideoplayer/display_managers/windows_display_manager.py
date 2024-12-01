import ctypes
from ctypes.wintypes import LPCWSTR, HWND
from pathlib import Path

from .abstract_display_manager import DisplayManager
from ..utils.windows_os_utils import set_icon_windows


class WindowsDisplayManager(DisplayManager):
    def __init__(self):
        ctypes.windll.shcore.SetProcessDpiAwareness(2)

    def get_screen_size(self):
        user32 = ctypes.windll.user32
        screensize = 0.9 * user32.GetSystemMetrics(0), 0.9 * user32.GetSystemMetrics(1)
        return screensize

    def get_in_focus_window_id(self):
        h_wnd = ctypes.windll.user32.GetForegroundWindow()
        pid = ctypes.wintypes.DWORD()
        ctypes.windll.user32.GetWindowThreadProcessId(h_wnd, ctypes.byref(pid))
        return pid.value

    def get_player_window_id(self, window_name):
        user32 = ctypes.windll.user32
        user32.FindWindowW.argtypes = [LPCWSTR, LPCWSTR]
        user32.FindWindowW.restype = HWND
        h_wnd = user32.FindWindowW(None, window_name)
        pid = ctypes.wintypes.DWORD()
        ctypes.windll.user32.GetWindowThreadProcessId(h_wnd, ctypes.byref(pid))
        return pid.value

    def set_icon(self, window_name, **kwargs):
        set_icon_windows(window_name, icon_path=Path(__file__).parent.parent / "icon.png")
