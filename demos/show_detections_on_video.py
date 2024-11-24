from pathlib import Path
from demo_utils import add_project_root_to_path, change_cwd_to_demos_dir

add_project_root_to_path()
change_cwd_to_demos_dir()

from cvvideoplayer import create_video_player
from cvvideoplayer.frame_editors import (
    KeyMapOverlay,
    DetectionsCsvPlotter,
    FrameInfoOverlay,
    FitFrameToScreen,
)


def run_player():
    video_player = create_video_player(
        video_source="../assets/example_video.mp4",
        record=True,
        frame_edit_callbacks=[
            FitFrameToScreen(),
            DetectionsCsvPlotter(detections_csv_path=Path("../assets/example_video_detections.csv")),
            KeyMapOverlay(),
            FrameInfoOverlay(),
        ],
    )

    video_player.run()


if __name__ == "__main__":
    run_player()
