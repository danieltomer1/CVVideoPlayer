from typing import List, TYPE_CHECKING, Optional

import numpy as np

from ..utils.video_player_utils import KeyFunction

if TYPE_CHECKING:
    from ..video_players.base_video_player import VideoPlayer


class BaseFrameEditCallback:

    def __init__(
            self,
            enable_by_default: bool,
            enable_disable_key: Optional[str] = None,
            additional_keyboard_shortcuts: Optional[List[KeyFunction]] = None
    ):
        self._enabled = enable_by_default
        self._enable_disable_key = enable_disable_key
        self._additional_keyboard_shortcuts = additional_keyboard_shortcuts

    """
    All implemented callbacks need to inherit this Base class
    params:
        enable_by_default (bool): If True enable the callback on video start
        enable_disable_key (str): Optional keyboard shortcut to disable/enable the callback in runtime
    """
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
        key_function_list = []
        if self._enable_disable_key is not None:
            key_function_list.append(KeyFunction(
                key=self._enable_disable_key,
                func=self.enable_disable,
                description=f"Enable/Disable {self.__class__.__name__}"
            ))
        if self._additional_keyboard_shortcuts is not None:
            assert all([isinstance(item, KeyFunction) for item in self._additional_keyboard_shortcuts])
            key_function_list.extend(self._additional_keyboard_shortcuts)
        return key_function_list
