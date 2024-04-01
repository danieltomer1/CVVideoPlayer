from pathlib import Path
from cvvideoplayer import LocalFrameReader, Recorder, VideoPlayer
from cvvideoplayer.frame_editors.detections_csv_plotter import DetectionsCsvPlotter

CONFIG = {
    "source_path": "assets/example_video.mp4",
    "detection_csv_path": "assets/example_video_detections.csv",
    "recorder": {"enable": True},
}


def run_player():
    video_player = VideoPlayer(
        video_name=Path(CONFIG["source_path"]).stem,
        frame_reader=LocalFrameReader(source_path=CONFIG["source_path"]),
        recorder=Recorder() if CONFIG["recorder"]["enable"] else None,
        add_basic_frame_editors=True,
    )

    video_player.add_frame_editor(
        DetectionsCsvPlotter(
            detections_csv_path=Path(CONFIG["detection_csv_path"]),
        )
    )
    with video_player:
        video_player.run()


if __name__ == "__main__":
    run_player()
