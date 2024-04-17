from pathlib import Path
from cvvideoplayer import LocalFrameReader, Recorder, VideoPlayer
from cvvideoplayer.frame_editors.detections_csv_plotter import DetectionsCsvPlotter
from cvvideoplayer.frame_editors import FrameInfoOverlay, KeyMapOverlay
from cvvideoplayer.input_manager import InputManager

CONFIG = {
    "source_path": "assets/example_video.mp4",
    "detection_csv_path": "assets/example_video_detections.csv",
    "use_recorder":  True,
}


def run_player():
    video_player = VideoPlayer(
        video_name=Path(CONFIG["source_path"]).stem,
        frame_reader=LocalFrameReader(source_path=CONFIG["source_path"]),
        recorder=Recorder() if CONFIG["use_recorder"] else None,
        add_basic_frame_editors=False,
    )

    video_player.add_frame_editor(
        DetectionsCsvPlotter(
            detections_csv_path=Path(CONFIG["detection_csv_path"]),
        )
    )

    video_player.add_frame_editor(
        FrameInfoOverlay(
            top_left_coordinate=(10,10)
        ))

    video_player.add_frame_editor(
        KeyMapOverlay(
            top_left_coordinate=(60, 10)
        ))

    InputManager().print_keymap()

    with video_player:
        video_player.run()


if __name__ == "__main__":
    run_player()
