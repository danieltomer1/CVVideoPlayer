import numpy as np

from test_utils import change_cwd_to_tests_dir, add_project_root_to_path

change_cwd_to_tests_dir()
add_project_root_to_path()

from cvvideoplayer import TestingFrameReader, create_video_player
from cvvideoplayer.utils.ui_utils import SingleInput, InputType


def test_video_navigation():
    frame_reader = TestingFrameReader(video_len=70)
    video_player = create_video_player(
        video_source=frame_reader,
        start_from_frame=5
    )
    assert np.all(video_player._get_current_frame() == frame_reader.get_frame(5))
    video_player.input_handler.handle_input(SingleInput(InputType.KeyPress, "right"))
    assert np.all(video_player._get_current_frame() == frame_reader.get_frame(6))
    video_player.input_handler.handle_input(SingleInput(InputType.KeyPress, "ctrl+right"))
    assert np.all(video_player._get_current_frame() == frame_reader.get_frame(16))
    video_player.input_handler.handle_input(SingleInput(InputType.KeyPress, "ctrl+right"))
    assert np.all(video_player._get_current_frame() == frame_reader.get_frame(26))
    video_player.input_handler.handle_input(SingleInput(InputType.KeyPress, "ctrl+shift+right"))
    assert np.all(video_player._get_current_frame() == frame_reader.get_frame(69))
    video_player.input_handler.handle_input(SingleInput(InputType.KeyPress, "ctrl+shift+left"))
    assert np.all(video_player._get_current_frame() == frame_reader.get_frame(19))
    video_player.input_handler.handle_input(SingleInput(InputType.KeyPress, "ctrl+left"))
    assert np.all(video_player._get_current_frame() == frame_reader.get_frame(9))
    video_player.input_handler.handle_input(SingleInput(InputType.KeyPress, "ctrl+left"))
    assert np.all(video_player._get_current_frame() == frame_reader.get_frame(0))
    video_player.input_handler.handle_input(SingleInput(InputType.KeyPress, "left"))
    assert np.all(video_player._get_current_frame() == frame_reader.get_frame(0))
    video_player.input_handler.handle_input(SingleInput(InputType.KeyPress, "esc"))
    video_player.__exit__()
