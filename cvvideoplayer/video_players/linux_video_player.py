import subprocess
import time
from pathlib import Path

import Xlib
from Xlib import X

from ..input_management.linux_input_parser import LinuxInputParser
from ..utils.linux_os_utils import set_icon_linux
from .base_video_player import VideoPlayer


class LinuxVideoPlayer(VideoPlayer):
    def __init__(self, **video_player_kwargs):
        super().__init__(**video_player_kwargs)
        self._display = Xlib.display.Display()

    @property
    def _input_parser(self):
        return LinuxInputParser()

    def _get_in_focus_window_id(self):
        window = self._display.get_input_focus().focus
        if isinstance(window, int):
            return ""
        return window.id

    def _get_player_window_id(self):
        time.sleep(0.05)
        d = Xlib.display.Display()
        root = d.screen().root

        # Get all the window IDs on the current display
        window_ids = root.get_full_property(d.intern_atom('_NET_CLIENT_LIST'), X.AnyPropertyType).value
        for window_id in window_ids:
            # Get the window object
            window = d.create_resource_object('window', window_id)

            # Get the window name
            name = window.get_wm_name()
            if name and self._window_name in name:
                return window_id

    def _get_screen_size(self):
        screen_size_str = (
            subprocess.check_output('xrandr | grep "\*" | cut -d" " -f4', shell=True).decode().strip().split("\n")[0]
        )
        screen_w, screen_h = screen_size_str.split("x")
        screen_w = 0.85 * int(screen_w)
        screen_h = 0.85 * int(screen_h)
        return screen_w, screen_h

    def _set_icon(self):
        set_icon_linux(self._window_id, self._display, icon_path=str(Path(__file__).parent.parent / "icon.png"))
