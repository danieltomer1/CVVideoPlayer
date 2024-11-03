from demo_utils import change_cwd_to_demos_dir, add_project_root_to_path

change_cwd_to_demos_dir()
add_project_root_to_path()

from cvvideoplayer import LocalFrameReader, VideoPlayer
from cvvideoplayer.frame_editors import FrameInfoOverlay, KeyMapOverlay, FrameNormalizer, HistogramEqualizer


def run_player():
    frame_reader = LocalFrameReader(source_path="../assets/example_video.mp4")
    video_player = VideoPlayer(
        video_source=frame_reader,
        record=True,
        frame_edit_callbacks=[
            FrameNormalizer(),
            HistogramEqualizer(),
            FrameInfoOverlay(),
            KeyMapOverlay(),
        ],
    )

    with video_player:
        video_player.run()


if __name__ == "__main__":
    run_player()
