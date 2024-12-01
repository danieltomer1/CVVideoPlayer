import csv
from collections import defaultdict
from pathlib import Path
import typing as t

from ..frame_editors import BaseBboxPlotter
from ..utils.bbox_utils import Bbox


class DetectionsCsvPlotter(BaseBboxPlotter):
    """
    frame editor that plots detection given aa a csv is the following format:
    frame_id,label,x1,y1,width,height,score
    """

    def __init__(
        self,
        detections_csv_path: Path,
        enable_by_default: bool = True,
        enable_disable_key: str = "d",
        **bbox_plotter_kwargs,
    ):
        super().__init__(enable_by_default, enable_disable_key, **bbox_plotter_kwargs)

        self._detections = defaultdict(list)
        with detections_csv_path.open(newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                bbox = Bbox(
                    x1=int(float(row["x1"])),
                    y1=int(float(row["y1"])),
                    width=int(float(row["width"])),
                    height=int(float(row["height"])),
                    above_label=f"{row['label']} p: {float(row['score']):.2f}",
                    color=self._default_bbox_color,
                )
                self._detections[int(row["frame_id"])].append(bbox)

    def get_bboxes(self, frame_num, **kwargs) -> t.List[Bbox]:
        return self._detections[frame_num]
