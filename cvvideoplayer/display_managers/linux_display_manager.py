import subprocess
import time
from pathlib import Path

import Xlib
from Xlib import X

from .abstract_display_manager import DisplayManager
from ..utils.linux_os_utils import set_icon_linux


class LinuxDisplayManager(DisplayManager):
    def __init__(self):
        self._display = Xlib.display.Display()

    def get_in_focus_window_id(self):
        window = self._display.get_input_focus().focus
        if isinstance(window, int):
            return ""
        return window.id

    def get_player_window_id(self, window_name):
        time.sleep(0.05)
        root = self._display.screen().root

        # Get all the window IDs on the current display
        window_ids = root.get_full_property(self._display.intern_atom('_NET_CLIENT_LIST'), X.AnyPropertyType).value
        for window_id in window_ids:
            # Get the window object
            window = self._display.create_resource_object('window', window_id)

            # Get the window name
            name = window.get_wm_name()
            if name and window_name in name:
                return window_id

    def get_screen_size(self):
        screen_size_str = (
            subprocess.check_output('xrandr | grep "\*" | cut -d" " -f4', shell=True).decode().strip().split("\n")[0]
        )
        screen_w, screen_h = screen_size_str.split("x")
        screen_w = 0.85 * int(screen_w)
        screen_h = 0.85 * int(screen_h)
        return screen_w, screen_h

    def set_icon(self, window_id, **kwargs):
        set_icon_linux(window_id, self._display, icon_path=str(Path(__file__).parent.parent / "icon.png"))
