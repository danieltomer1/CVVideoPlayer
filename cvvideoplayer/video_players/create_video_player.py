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


def create_video_player(
        video_source: Union[str, Path, FrameReader],
        start_from_frame: int = 0,
        frame_edit_callbacks: Optional[List[BaseFrameEditCallback]] = None,
        record: Union[bool, AbstractRecorder] = False,
) -> VideoPlayer:
    """
    Params:
    - video_source : Union[str, Path, FrameReader] The source of the video to be played. It can be a file path, a
     directory path, or a FrameReader instance.
    - start_from_frame : int, optional The frame number to start the video from (default is 0).
    - frame_edit_callbacks : list, optional A list of frame editing callbacks (default is None).
     Each callback must be an instance of BaseFrameEditCallback.
    - record : Union[bool, AbstractRecorder], optional Whether to record the video or not (default is False).
    It can also be an instance of AbstractRecorder for custom recording functionality.
    """
    if CURRENT_OS == SupportedOS.WINDOWS:
        video_player_class = WindowsVideoPlayer

    elif CURRENT_OS == SupportedOS.LINUX:
        video_player_class = LinuxVideoPlayer

    else:
        raise ValueError(f"Unsupported OS: {CURRENT_OS}")

    return video_player_class(
        video_source=video_source,
        start_from_frame=start_from_frame,
        frame_edit_callbacks=frame_edit_callbacks,
        record=record,
    )


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
