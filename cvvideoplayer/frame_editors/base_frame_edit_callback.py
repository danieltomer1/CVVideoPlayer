from typing import List, TYPE_CHECKING

import numpy as np

from ..utils.video_player_utils import KeyFunction

if TYPE_CHECKING:
    from ..video_player import VideoPlayer


class BaseFrameEditCallback:

    def __init__(self, enable_by_default):
        self._enabled = enable_by_default

    @property
    def enabled(self):
        return self._enabled

    def setup(self, video_player: "VideoPlayer", frame) -> None:
        """
        Optionally configure more parameters according to the first incoming frame
        """

    def teardown(self) -> None:
        """
        Optionally define how the editor should close when video player is closed
        """

    def before_frame_resize(self, video_player: "VideoPlayer", frame: np.ndarray, frame_num: int) -> np.ndarray:
        """
        This function receives the frame before it has been resized and should return the frame
        after it has been altered in any way desirable by the user. In this hook you ere not allowed to change the
        frame's size.

        Args:
            video_player: an instance fo VideoPlayer
            frame (): the input frame
            frame_num ():

        Returns: the edited frame
        """
        return frame

    def after_frame_resize(self, video_player: "VideoPlayer", frame: np.ndarray, frame_num: int) -> np.ndarray:
        """
        This function receives the frame after it has been resized to fit the screen size and should return the frame
        after it has been altered in any way desirable by the user

        Args:
            video_player: an instance fo VideoPlayer
            frame (): the input frame
            frame_num ():

        Returns: the edited frame
        """
        return frame

    def enable_disable(self):
        self._enabled = not self._enabled

    @property
    def key_function_to_register(self) -> List[KeyFunction]:
        """
        Optionally return a list of KeyFunctions to be registered once the frame editor is added to the video player
        Examples:
            1. [
                  KeyFunction(
                      key="ctrl+f",  # A standard key combination can be any combination of modifiers with a single key
                      func=self.enable_disable,  # A function that receives no input
                      description="disable enable"  # A description of whatever this frame editor does
                  ),
                  KeyFunction(
                      key="ctrl+num", # A general num function that handles any number press
                      func=self._change_id, # this function needs to receive the number as an input
                      description="change the printed id according to the number pressed"
                  )
              ]
        """
        return []
