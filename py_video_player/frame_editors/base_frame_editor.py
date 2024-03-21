from abc import ABC, abstractmethod
from typing import Dict, Optional

import numpy as np

from py_video_player.frame_editors.abstract_frame_editor import AbstractFrameEditor
from py_video_player.utils.video_player_utils import KeymapAction


class BaseFrameEditor(AbstractFrameEditor, ABC):

    def __init__(self, enable_by_default):
        self._enabled = enable_by_default

    def enable_disable(self):
        self._enabled = bool(1 - self._enabled)

    @property
    @abstractmethod
    def edit_after_resize(self) -> bool:
        pass

    @property
    def keymap_actions_to_register(self) -> Optional[Dict[str, KeymapAction]]:
        return None

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

    def edit_frame(self, frame: np.ndarray, frame_num: int) -> np.ndarray:
        if not self._enabled:
            return frame
        else:
            return self._edit_frame(frame, frame_num)
