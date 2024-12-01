from pathlib import Path
from typing import Union, Optional, List

from .base_video_player import VideoPlayer
from .. import FrameReader, AbstractRecorder
from ..frame_editors import BaseFrameEditCallback
from ..utils.video_player_utils import SupportedOS, CURRENT_OS

if CURRENT_OS == SupportedOS.LINUX:
    from .linux_video_player import LinuxVideoPlayer, LinuxDoubleFrameVideoPlayer
    from ..display_managers.linux_display_manager import LinuxDisplayManager

elif CURRENT_OS == SupportedOS.WINDOWS:
    from .windows_video_player import WindowsVideoPlayer, WindowsDoubleFrameVideoPlayer
    from ..display_managers.windows_display_manager import WindowsDisplayManager


def create_video_player(
        video_source: Union[str, Path, FrameReader],
        start_from_frame: int = 0,
        frame_edit_callbacks: Optional[List[BaseFrameEditCallback]] = None,
        record: Union[bool, AbstractRecorder] = False,
        double_frame_mode: bool = False,
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
        display_manager = WindowsDisplayManager()
        if double_frame_mode:
            video_player_class = WindowsDoubleFrameVideoPlayer
        else:
            video_player_class = WindowsVideoPlayer

    elif CURRENT_OS == SupportedOS.LINUX:
        display_manager = LinuxDisplayManager()
        if double_frame_mode:
            video_player_class = LinuxDoubleFrameVideoPlayer
        else:
            video_player_class = LinuxVideoPlayer

    else:
        raise ValueError(f"Unsupported OS: {CURRENT_OS}")

    return video_player_class(
        video_source=video_source,
        start_from_frame=start_from_frame,
        frame_edit_callbacks=frame_edit_callbacks,
        record=record,
        display_manager=display_manager
    )
