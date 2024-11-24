<div align="center"><img src=https://github.com/user-attachments/assets/88f4e3af-0fd3-41dc-9515-85a58dfdf2fc width="250"></div>

## Introduction
CV video player is a Python-based customizable video player that helps computer vision practitioners
develop, analyze, and debug their video-related algorithms and models.

The video player is made with simplicity in mind to allow users to easily add or remove functionality.
It is only based OpenCV with no additional GUI frameworks, and
It's interactivity is based on keyboard presses (no buttons).

The player is designed as a callback system. When initialized the player receives a 
list of callbacks, each with a `edit_frame` method.
On runtime the callbacks will run in order as specified in the input list. Each callback can also optionally add 
keyboard shortcuts to change visualization settings in real time.

## Installation
`pip install cvvideoplayer`

## Quick Start

```python
from cvvideoplayer import create_video_player
from cvvideoplayer.frame_editors import FrameInfoOverlay, KeyMapOverlay, FitFrameToScreen

VIDEO_OR_FRAME_FOLDER_PATH = "<add local path here>"


def run_player():
    video_player = create_video_player(
        video_source=VIDEO_OR_FRAME_FOLDER_PATH,
        frame_edit_callbacks=[
            FitFrameToScreen(),
            FrameInfoOverlay(),
            KeyMapOverlay(),
        ],
        record=True,
    )

    video_player.run()


if __name__ == "__main__":
    run_player()
``` 

In this example, we initiate a very basic video player that will play "example_video.mp4" with added basic
frame edit callbacks:
- `FitFrameToScreen`: Resizes the frame to fit the screen size
- `FrameInfoOverlay`: Prints the current frame number and original frame resolution in the top left corner
- `KeyMapOverlay`: prints all optional shortcuts registered by all callbacks

Check out the `./demos` folder which shows the use of other cool frame edit callback
such as `OpticalFlow` and `DetectionCsvPlotter`
## See it in action
<details>
<summary>Running frame by frame</summary>
    
![frame_by_frame](https://github.com/danieltomer1/CVVideoPlayer/assets/163285251/7db8cb8c-0075-416c-9901-aa2f4bb49080)
</details>

<details>
<summary>Play/Pause and control play speed and direction</summary>
    
![playpause](https://github.com/danieltomer1/CVVideoPlayer/assets/163285251/fcf38b37-ec9c-4250-8c2f-6f123154c1e4)
</details>

<details>
<summary>Draw bounding boxes and adjust labels</summary>
    
![bboxes](https://github.com/danieltomer1/CVVideoPlayer/assets/163285251/0a6e07de-a015-48b4-b510-2c203e0d69f4)
</details>


