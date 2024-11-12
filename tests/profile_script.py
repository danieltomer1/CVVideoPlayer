import cProfile

from test_utils import change_cwd_to_tests_dir, add_project_root_to_path

change_cwd_to_tests_dir()
add_project_root_to_path()

from cvvideoplayer import create_video_player
from cvvideoplayer.utils.ui_utils import SingleInput, InputType


def main():
    key_recordings = ["right"] * 200 + ["esc"]
    for key in key_recordings:
        video_player._input_parser._ui_queue.put(SingleInput(InputType.KeyPress, key))
    video_player._run_player_loop()


if __name__ == "__main__":
    video_player = create_video_player(video_source="../assets/example_video.mp4")
    video_player._open_player()
    cProfile.run("main()", "profile_output.prof")
