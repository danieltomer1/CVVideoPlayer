from .double_frame_video_player import DoubleFrameVideoPlayer
from ..input_management.linux_input_parser import LinuxInputParser
from .base_video_player import VideoPlayer


class LinuxVideoPlayer(VideoPlayer):
    @property
    def _input_parser(self):
        return LinuxInputParser()


class LinuxDoubleFrameVideoPlayer(DoubleFrameVideoPlayer):
    @property
    def _input_parser(self):
        return LinuxInputParser()

