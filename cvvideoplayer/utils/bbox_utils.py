from dataclasses import dataclass
from enum import Enum
from typing import Tuple, Optional


class BboxFormat(Enum):
    xywh = "xywh"  # x_min, y_min, width, height
    xyxy = "xyxy"  # x_min, y_min, x_max, y_max
    xcycwh = "xcycwh"  # x_center, y_center, width, height


@dataclass
class Bbox:
    x1: int
    y1: int
    width: int
    height: int
    color: Optional[Tuple[int, int, int]] = None
    above_label: Optional[str] = None
    below_label: Optional[str] = None

    @classmethod
    def init_with_xyxy(cls, x1, y1, x2, y2, color=None, above_label=None, below_label=None):
        return cls(x1, y1, x2 - x1, y2 - y1, color, above_label, below_label)

    @property
    def x2(self):
        return self.x1 + self.width

    @property
    def y2(self):
        return self.y1 + self.height

    @property
    def x_center(self):
        return self.x1 + (self.width / 2)

    @property
    def y_center(self):
        return self.y1 + (self.height / 2)

    @property
    def area(self):
        return self.width * self.height

    def get_normalized_bbox(
            self,
            frame_width: int,
            frame_height: int,
            bbox_format: BboxFormat = BboxFormat.xywh
    ) -> Tuple[float, float, float, float]:
        frame_width = float(frame_width)
        frame_height = float(frame_height)
        if bbox_format == BboxFormat.xywh:
            return self.x1 / frame_width, self.y1 / frame_height, self.width / frame_width, self.height / frame_height
        if bbox_format == BboxFormat.xyxy:
            return self.x1 / frame_width, self.y1 / frame_height, self.x2 / frame_width, self.y2 / frame_height
        if bbox_format == BboxFormat.xcycwh:
            return self.x_center / frame_width, self.y_center / frame_height, self.width / frame_width, self.height / frame_height
