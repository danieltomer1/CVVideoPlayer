from pathlib import Path
from cvvideoplayer import LocalFrameReader, Recorder, VideoPlayer
from cvvideoplayer.frame_editors.detections_csv_plotter import DetectionsCsvPlotter
from cvvideoplayer.frame_editors import FrameNumPrinter

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
        FrameNumPrinter(
            bottom_left_coordinate=(100,0) # I think it should be named top_left_coordinate
        ))

    with video_player:
        video_player.run()


if __name__ == "__main__":
    run_player()
