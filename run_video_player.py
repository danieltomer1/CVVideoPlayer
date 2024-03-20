from pathlib import Path
from py_video_player import LocalFrameReader, Recorder, VideoPlayer

CONFIG = {
    "source_path": "sample_videos/sample_video.mp4",
    "recorder": {
        "enable": True,
    },
}


def run_player():
    frame_reader = LocalFrameReader(source_path=CONFIG["source_path"])
    video_name = Path(CONFIG["source_path"]).stem

    recorder = Recorder() if CONFIG["recorder"]["enable"] else None

    video_player = VideoPlayer(
        video_name=video_name,
        frame_reader=frame_reader,
        recorder=recorder,
    )

    with video_player:
        video_player.run()


if __name__ == "__main__":
    run_player()
