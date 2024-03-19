from pathlib import Path

from py_video_player import ImageReader, Recorder, VideoPlayer

CONFIG = {
    "data_source": "local_video_path",
    "local_video_path": "sample_videos/sample_video.mp4",
    "recorder": {"enable": False},
}


def get_video_name(data_source_name, data_source_path):
    if data_source_name == "remote_video_dir":
        video_name = data_source_path.replace("s3://", "")
    elif data_source_name == "local_video_path":
        video_name = Path(data_source_path).stem
    else:
        raise Exception(f"cfg.data_source = {data_source_name} not supported for running single video")
    return video_name


def run_player():
    image_reader = ImageReader(data_source_name=CONFIG["data_source"], data_source_path=CONFIG[CONFIG["data_source"]])
    video_name = get_video_name(data_source_name=CONFIG["data_source"], data_source_path=CONFIG[CONFIG["data_source"]])

    recorder = (
        Recorder(
            output_video_path=Path(CONFIG["recorder"]["output_video_folder"]) / video_name / "_with_gt.mp4",
            recorded_video_fps=CONFIG["recorder"]["recorded_video_fps"],
            output_video_shape=CONFIG["recorder"]["output_video_shape"],
        )
        if CONFIG["recorder"]["enable"]
        else None
    )

    video_player = VideoPlayer(
        video_name=video_name,
        image_reader=image_reader,
        recorder=recorder,
    )

    with video_player:
        video_player.run()


if __name__ == "__main__":
    run_player()
