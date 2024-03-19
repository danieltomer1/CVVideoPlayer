from abc import ABC, abstractmethod

import numpy as np


class AbstractFrameEditor(ABC):
    # @property
    # @abstractmethod
    # def keyboard_press_dict(self) -> Dict[str, Callable]:
    #     """
    #     Returns the dictionary that defines how keyboard presses affect the editor's visualization parameters.
    #     The keyboard press dict should have the following structure:
    #     dict(
    #         <key_name>: <function>
    #     )
    #     where <key_name> is lower case and should look like: "s", "ctrl+d", "shift+alt+r", etc.
    #     to handle a number press the key_name should be: "int", "ctrl+int", "shift+int", etc.
    #
    #     <function> is a callable function which takes the key as input. For numbers, the number pressed will be
    #     passed to the function which allows the user to designate a single function to handle all number presses.
    #     """
    #     pass

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
