from dataclasses import dataclass
from enum import Enum
from typing import Tuple, Optional, Union


class BboxFormat(Enum):
    xywh = "xywh"  # x_min, y_min, width, height
    xyxy = "xyxy"  # x_min, y_min, x_max, y_max
    xcycwh = "xcycwh"  # x_center, y_center, width, height


@dataclass
class Bbox:
    x1: Union[int, float]
    y1: Union[int, float]
    width: Union[int, float]
    height: Union[int, float]
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

    def get_normalized_bbox(self, frame_width: int, frame_height: int) -> "Bbox":
        frame_width = float(frame_width)
        frame_height = float(frame_height)
        x1 = self.x1 / frame_width
        y1 = self.y1 / frame_height
        width = self.width / frame_width
        height = self.height / frame_height
        return Bbox(x1, y1, width, height, self.color)
