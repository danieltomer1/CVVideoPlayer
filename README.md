<div align="center"><img src="assets/logo.png" width="150"></div>

## Introduction
CV video player is a python-based customizable video player that helps computer vision practitioners
to develop, anlalyze and debug their video related algorithms and model


## Installation
`pip install cvvideoplayer`

## Usage
The player is interactive and operates only with keyboard presses (no buttons). The user can register new 
shortcuts using the VideoPlayer class's API.

The user can also add FrameEditors to the player which is a class that needs to inherit BaseFrameEditor and
implement the following abstract methods:
```python
class BaseFrameEditor(ABC):
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
```

## Quick Start
```python
from cvvideoplayer import LocalFrameReader, Recorder, VideoPlayer


def run_player():
    video_player = VideoPlayer(
        video_name="example_video",
        frame_reader=LocalFrameReader(source_path="assets/example_video.mp4"),
        recorder=Recorder(),
        add_basic_frame_editors=True,
    )

    with video_player:
        video_player.run()


if __name__ == "__main__":
    run_player()
``` 

In this example we initiate a very basic video player that will play "example_video.mp4" with basic functionalities such as:

- 