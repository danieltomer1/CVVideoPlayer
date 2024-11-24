import argparse
from pathlib import Path
from typing import List
import sys
from cvvideoplayer.frame_editors import (
    BaseFrameEditCallback,
    FrameInfoOverlay,
    OpticalFlowPlotter,
    FrameSnapshot
)

import inspect
from cvvideoplayer.utils.ui_utils import InputType, SingleInput
from cvvideoplayer.video_players.base_video_player import VideoPlayer
from cvvideoplayer import create_video_player
import cv2


TEST_ASSETS_DIR = Path(__file__).parent / "expected_images"


# python sucks
def plus_plus(integer_in_list_wrapper: List[int]):
    res = integer_in_list_wrapper[0]
    integer_in_list_wrapper[0] += 1
    return res


def create_video_player_for_snapshot(
    source_path: Path,
    output_path,
    frame_num: int,
    frame_edit_callbacks: List[BaseFrameEditCallback] = None,
):
    video_player = create_video_player(
        video_source=Path(source_path),
        frame_edit_callbacks=frame_edit_callbacks + [FrameSnapshot(output_path, (300, 200), frame_num)],
    )

    return video_player


def take_snapshot(video_player: VideoPlayer, key_recordings: List[str]):
    video_player._open_player()
    for key in key_recordings:
        video_player._input_parser._ui_queue.put(SingleInput(InputType.KeyPress, key))

    video_player._run_player_loop()
    cv2.destroyAllWindows()


def compare_images(expected_path: Path, actual_path: Path, diff_path: Path):
    assert actual_path.exists(), f"Something went wrong, the actual image was not saved at {actual_path}"
    # assert that the two images are the same
    expected_frame = cv2.imread(str(expected_path))
    actual_frame = cv2.imread(str(actual_path))
    frame_diff = cv2.absdiff(expected_frame, actual_frame)
    if frame_diff.any():
        cv2.imwrite(str(diff_path), frame_diff)
        return False
    return True


def run_test(
    key_recordings: List[str],
    frame_num,
    record: bool,
    test_name: str,
    frame_edit_callbacks: List[BaseFrameEditCallback] = None,
):
    expected_path = TEST_ASSETS_DIR / f"{test_name}_expected.png"
    actual_path = TEST_ASSETS_DIR / f"{test_name}_actual.png"
    diff_path = TEST_ASSETS_DIR / f"{test_name}_diff.png"
    video_player = create_video_player_for_snapshot(
        source_path=Path(__file__).parent / "../assets/example_video.mp4",
        output_path=expected_path if record else actual_path,
        frame_num=frame_num,
        frame_edit_callbacks=frame_edit_callbacks,
    )

    if record:
        expected_path.unlink(missing_ok=True)
    actual_path.unlink(missing_ok=True)
    diff_path.unlink(missing_ok=True)
    take_snapshot(video_player, key_recordings)

    if not expected_path.exists():
        print(
            f"{test_name}: [ERROR] Expected image not found at {expected_path}, please run the test in record mode first",
            file=sys.stderr,
        )
        sys.exit(1)

    if not record:
        print(f"{test_name}: ", end="")
        res = compare_images(expected_path, actual_path, diff_path)
        if res:
            print("[PASS]")
        else:
            print(
                "[FAIL]",
                f"Expected image and actual image are different, diff image saved at {diff_path}",
            )


def test_simple_image(record=False):
    test_name = inspect.currentframe().f_code.co_name
    frame_edit_callbacks = []

    test_idx = [0]

    frame_num = 3
    key_recordings = ["right" for _ in range(frame_num)] + ["esc"]

    run_test(
        key_recordings,
        frame_num,
        record,
        f"{test_name}_{plus_plus(test_idx)}",
        frame_edit_callbacks,
    )

    frame_num = 10
    key_recordings = ["ctrl+right"] + ["esc"]

    run_test(
        key_recordings,
        frame_num,
        record,
        f"{test_name}_{plus_plus(test_idx)}",
        frame_edit_callbacks,
    )


def test_frame_info_overlay(record=False):
    test_name = inspect.currentframe().f_code.co_name
    frame_edit_callbacks = [FrameInfoOverlay()]

    test_idx = [0]

    frame_num = 15
    key_recordings = ["right" for _ in range(frame_num)] + ["esc"]

    run_test(
        key_recordings,
        frame_num,
        record,
        f"{test_name}_{plus_plus(test_idx)}",
        frame_edit_callbacks,
    )

    frame_num = 7
    key_recordings = ["right" for _ in range(frame_num)] + ["esc"]

    run_test(
        key_recordings,
        frame_num,
        record,
        f"{test_name}_{plus_plus(test_idx)}",
        frame_edit_callbacks,
    )

    frame_num = 3
    key_recordings = ["right" for _ in range(frame_num)] + [
        "ctrl+f",
        "esc",
    ]

    run_test(
        key_recordings,
        frame_num,
        record,
        f"{test_name}_{plus_plus(test_idx)}",
        frame_edit_callbacks,
    )


def test_optical_flow(record=False):
    test_name = inspect.currentframe().f_code.co_name
    frame_edit_callbacks = [OpticalFlowPlotter(enable_by_default=True)]

    test_idx = [0]

    frame_num = 15
    key_recordings = ["right" for _ in range(frame_num)] + [
        "esc",
    ]

    run_test(
        key_recordings,
        frame_num,
        record,
        f"{test_name}_{plus_plus(test_idx)}",
        frame_edit_callbacks,
    )

    frame_num = 7
    key_recordings = ["right" for _ in range(frame_num)] + ["esc"]

    run_test(
        key_recordings,
        frame_num,
        record,
        f"{test_name}_{plus_plus(test_idx)}",
        frame_edit_callbacks,
    )

    frame_num = 3
    key_recordings = ["right" for _ in range(frame_num)] + [
        "esc",
    ]

    run_test(
        key_recordings,
        frame_num,
        record,
        f"{test_name}_{plus_plus(test_idx)}",
        frame_edit_callbacks,
    )


def run(record=False):
    TEST_ASSETS_DIR.mkdir(exist_ok=True)
    test_simple_image(record)
    test_frame_info_overlay(record)
    test_optical_flow(record)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="record expected images from the player and replay against a new implementation to show differences in the output",
        allow_abbrev=False,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--record", action="store_true", default=False, help="Record expected images")
    group.add_argument("--replay", action="store_true", default=False, help="Replay and run the tests")

    args = parser.parse_args()

    run(args.record and not args.replay)
