from pathlib import Path
from cvvideoplayer import LocalFrameReader, Recorder, VideoPlayer
from cvvideoplayer.frame_editors import FrameInfoOverlay, KeyMapOverlay, FrameNormalizer, HistogramEqualizer
from cvvideoplayer.frame_editors.detections_csv_plotter import DetectionsCsvPlotter


CONFIG = {
    "source_path": "assets/example_video.mp4",
    "detection_csv_path": "assets/example_video_detections.csv",
    "recorder": {"enable": True},
}


def run_player():
    frame_reader = LocalFrameReader(source_path=CONFIG["source_path"])
    video_player = VideoPlayer(
        video_name=Path(CONFIG["source_path"]).stem,
        frame_reader=frame_reader,
        recorder=Recorder() if CONFIG["recorder"]["enable"] else None,
        frame_edit_callbacks=[
            FrameInfoOverlay(video_total_frame_num=len(frame_reader)),
            FrameNormalizer(),
            HistogramEqualizer(),
            DetectionsCsvPlotter(detections_csv_path=Path(CONFIG["detection_csv_path"])),
            KeyMapOverlay(),
        ]
    )

    with video_player:
        video_player.run()


if __name__ == "__main__":
    run_player()
