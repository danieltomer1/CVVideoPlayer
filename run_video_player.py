from pathlib import Path
from py_video_player import LocalFrameReader, Recorder, VideoPlayer

CONFIG = {
    "source_path": "sample_videos/sample_video.mp4",
    "recorder": {"enable": True},
}


def run_player():
    video_player = VideoPlayer(
        video_name=Path(CONFIG["source_path"]).stem,
        frame_reader=LocalFrameReader(source_path=CONFIG["source_path"]),
        recorder=Recorder() if CONFIG["recorder"]["enable"] else None,
        add_basic_frame_editors=True,
    )

    with video_player:
        video_player.run()


if __name__ == "__main__":
    run_player()
