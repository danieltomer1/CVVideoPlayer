from abc import ABC, abstractmethod
from typing import Optional, List

import numpy as np

from ..utils.video_player_utils import KeyFunction


class BaseFrameEditor(ABC):

    def __init__(self, enable_by_default):
        self._enabled = enable_by_default

    @property
    @abstractmethod
    def edit_after_resize(self) -> bool:
        """
        Returns a boolean indicating whether the edit should happen before the frame is resized to fit the frame or
        after. True for after...
        """
        pass

    @abstractmethod
    def _edit_frame(self, frame: np.ndarray, frame_num: int) -> np.ndarray:
        """
        Here is where the editing happens. The function receives a frame and frame number and should return the frame
        after it has been altered in any way desirable by the user

        Args:
            frame (): the input frame
            frame_num ():

        Returns: the edited frame
        """
        pass

    def enable_disable(self):
        self._enabled = not self._enabled

    @property
    def key_function_to_register(self) -> Optional[List[KeyFunction]]:
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
        return None

    def edit_frame(self, frame: np.ndarray, frame_num: int) -> np.ndarray:
        if not self._enabled:
            return frame
        else:
            return self._edit_frame(frame, frame_num)

    def setup(self, frame) -> None:
        """
        Optionally configure more parameters according to the first incoming frame
        """
        return

    def teardown(self) -> None:
        """
        Optionally define how the editor should close when video player is closed
        """
        return
