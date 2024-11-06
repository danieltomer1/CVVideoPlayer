from demo_utils import change_cwd_to_demos_dir, add_project_root_to_path

change_cwd_to_demos_dir()
add_project_root_to_path()

from cvvideoplayer import VideoPlayer
from cvvideoplayer.frame_editors import FrameInfoOverlay, KeyMapOverlay, OpticalFlowPlotter


def run_player():
    video_player = VideoPlayer(
        video_source="../assets/example_video.mp4",
        record=True,
        frame_edit_callbacks=[
            FrameInfoOverlay(),
            KeyMapOverlay(),
            OpticalFlowPlotter(enable_by_default=True),
        ],
    )

    video_player.run()


if __name__ == "__main__":
    run_player()
