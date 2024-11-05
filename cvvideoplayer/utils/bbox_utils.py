from dataclasses import dataclass
import typing as t


@dataclass
class Bbox:
    x1: int
    y1: int
    width: int
    height: int
    color: t.Optional[t.Tuple[int, int, int]] = None
    above_label: t.Optional[str] = None
    below_label: t.Optional[str] = None

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
