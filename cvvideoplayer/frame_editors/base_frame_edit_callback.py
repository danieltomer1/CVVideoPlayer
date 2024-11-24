from typing import List, TYPE_CHECKING

import numpy as np

from ..utils.video_player_utils import KeyFunction

if TYPE_CHECKING:
    from ..video_players.base_video_player import VideoPlayer


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
        Optionally define how the callback should close when the video player is closed
        """

    def edit_frame(
            self,
            video_player: "VideoPlayer",
            frame: np.ndarray,
            frame_num: int,
            original_frame: np.ndarray,
    ) -> np.ndarray:
        """
        This function receives the displayed frame and should return it
        after it has been altered in any way desirable by the user

        Args:
            video_player: an instance fo VideoPlayer
            frame (): the frame to be edited and displayed
            frame_num ():
            original_frame () the frame before any alterations

        Returns: the edited frame
        """
        return frame

    def enable_disable(self):
        self._enabled = not self._enabled

    @property
    def key_function_to_register(self) -> List[KeyFunction]:
        """
        Optionally return a list of KeyFunctions to be registered once the frame editor is added to the video player
        Example:
            return [
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
