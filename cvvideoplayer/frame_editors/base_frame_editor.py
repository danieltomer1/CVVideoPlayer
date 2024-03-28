from abc import ABC, abstractmethod
from typing import Dict, Optional

import numpy as np

from ..utils.video_player_utils import KeymapAction


class BaseFrameEditor(ABC):

    def __init__(self, enable_by_default):
        self._enabled = enable_by_default

    def enable_disable(self):
        self._enabled = bool(1 - self._enabled)

    @property
    @abstractmethod
    def edit_after_resize(self) -> bool:
        pass

    @abstractmethod
    def _edit_frame(self, frame: np.ndarray, frame_num: int) -> np.ndarray:
        """
        Here is where the editing happens

        Args:
            frame (): the input frame
            frame_num ():

        Returns: the edited frame
        """
        pass

    @property
    def keymap_actions_to_register(self) -> Optional[Dict[str, KeymapAction]]:
        return None

    def edit_frame(self, frame: np.ndarray, frame_num: int) -> np.ndarray:
        if not self._enabled:
            return frame
        else:
            return self._edit_frame(frame, frame_num)

    def setup(self, frame) -> None:
        """
        Optionally configure the editors initialization parameters according to incoming frame
        """
        return

    def teardown(self) -> None:
        """
        Optionally define how the editor should close when video player is closed
        """
        return
