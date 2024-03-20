from abc import ABC, abstractmethod

import numpy as np


class AbstractFrameEditor(ABC):
    @property
    @abstractmethod
    def edit_after_resize(self) -> bool:
        """
        A boolean to indicate if the editor should preform its edit after frame is resized to fit screen.
        """
        pass

    @abstractmethod
    def edit_frame(self, frame: np.ndarray, frame_num: int) -> np.ndarray:
        """
        Here is where the editing happens

        Args:
            frame (): the input frame
            frame_num ():

        Returns: the edited frame
        """
        pass

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
