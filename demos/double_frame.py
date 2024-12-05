from demo_utils import change_cwd_to_demos_dir, add_project_root_to_path

change_cwd_to_demos_dir()
add_project_root_to_path()

from cvvideoplayer import create_video_player
from cvvideoplayer.frame_editors import (
    FrameInfoOverlay,
    FitFrameToScreen,
    BackgroundSub,
    KeyMapOverlay,
)


def run_player():
    video_player = create_video_player(
        video_source="../assets/example_video.mp4",
        record=True,
        frame_edit_callbacks=[
            FitFrameToScreen(),
            FrameInfoOverlay(),
            KeyMapOverlay(),
        ],
        double_frame_mode=True,
        right_frame_callbacks=[
            FitFrameToScreen(),
            BackgroundSub(enable_by_default=True),
        ],
    )

    video_player.run()


if __name__ == "__main__":
    run_player()
