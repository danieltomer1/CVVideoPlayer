from pathlib import Path
from demo_utils import add_project_root_to_path, change_cwd_to_demos_dir
add_project_root_to_path()
change_cwd_to_demos_dir()

from cvvideoplayer import VideoPlayer
from cvvideoplayer.frame_editors import KeyMapOverlay, DetectionsCsvPlotter


def run_player():
    video_player = VideoPlayer(
        video_source="../assets/example_video.mp4",
        record=True,
        frame_edit_callbacks=[
            DetectionsCsvPlotter(detections_csv_path=Path("../assets/example_video_detections.csv")),
            KeyMapOverlay(),
        ]
    )

    with video_player:
        video_player.run()


if __name__ == "__main__":
    run_player()
