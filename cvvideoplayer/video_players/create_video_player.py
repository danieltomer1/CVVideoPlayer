from pathlib import Path
from typing import Union, Optional, List

from .base_video_player import VideoPlayer
from .. import FrameReader, AbstractRecorder
from ..frame_editors import BaseFrameEditCallback
from ..utils.video_player_utils import SupportedOS, CURRENT_OS

if CURRENT_OS == SupportedOS.LINUX:
    from .linux_video_player import LinuxVideoPlayer

elif CURRENT_OS == SupportedOS.WINDOWS:
    from .windows_video_player import WindowsVideoPlayer


def create_video_player(**video_kwargs) -> VideoPlayer:
    if CURRENT_OS == SupportedOS.WINDOWS:
        return WindowsVideoPlayer(**video_kwargs)
    elif CURRENT_OS == SupportedOS.LINUX:
        return LinuxVideoPlayer(**video_kwargs)


class DeprecatedVideoPlayer:
    def __init__(
        self,
        video_source: Union[str, Path, FrameReader],
        start_from_frame: int = 0,
        frame_edit_callbacks: Optional[List[BaseFrameEditCallback]] = None,
        record: Union[bool, AbstractRecorder] = False,
    ):
        self._video_player = create_video_player(
            video_source=video_source,
            start_from_frame=start_from_frame,
            frame_edit_callbacks=frame_edit_callbacks,
            record=record,
        )

    def run(self) -> None:
        self._video_player.run()
