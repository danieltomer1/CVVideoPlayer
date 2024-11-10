from test_utils import change_cwd_to_tests_dir, add_project_root_to_path

change_cwd_to_tests_dir()
add_project_root_to_path()

from cvvideoplayer import VideoPlayer, InputParser
from cvvideoplayer.utils.ui_utils import SingleInput, InputType


if __name__ == "__main__":
    video_player = VideoPlayer(video_source="../assets/example_video.mp4")
    video_player._setup()
    key_recordings = ["right"] * 200 + ["esc"]
    for key in key_recordings:
        InputParser()._ui_queue.put(SingleInput(InputType.KeyPress, key))
    video_player._run_player_loop()