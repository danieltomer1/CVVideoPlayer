import csv
from collections import defaultdict
from pathlib import Path
import typing as t

from ..utils.video_player_utils import KeyFunction
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
        show_class_label=True,
        **bbox_plotter_kwargs,
    ):
        super().__init__(enable_by_default, show_above_bbox_label=show_class_label, **bbox_plotter_kwargs)

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

    @property
    def key_function_to_register(self):
        key_list = super().key_function_to_register
        key_list.append(KeyFunction(key="d", func=self.enable_disable, description="Show/Hide detections"))
        return key_list
