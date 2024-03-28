from abc import ABC, abstractmethod
from typing import *

from cvvideoplayer.frame_editors import BaseFrameEditor
from cvvideoplayer.utils.bbox_utils import Bbox
from cvvideoplayer.utils.drawing_utils import draw_rectangle, draw_label


class BaseBboxPlotter(BaseFrameEditor, ABC):
    def __init__(
        self,
        enable_by_default: bool = False,
        show_above_bbox_label: bool = True,
        show_below_bbox_label: bool = True,
        bbox_color: Tuple[int, int, int] = (255, 0, 0),
        text_color: Tuple[int, int, int] = (255, 255, 255),
        drawing_thickness: int = 1,
        font_scale: float = 0.5,
        label_text_color: Tuple[int, int, int] = (255, 255, 255),
        label_line_color: Optional[Tuple[int, int, int]] = None,
        label_filling_color: Tuple[int, int, int] = (0, 0, 0),
    ):
        super().__init__(enable_by_default)
        self._text_color = text_color
        self._font_scale = font_scale
        self._thickness = drawing_thickness
        self._show_above_bbox_label = show_above_bbox_label
        self._show_below_bbox_label = show_below_bbox_label
        self._bbox_color = bbox_color
        self._label_text_color = label_text_color
        self._label_line_color = label_line_color or bbox_color
        self._label_filling_color = label_filling_color

    @property
    def edit_after_resize(self) -> bool:
        return False

    @abstractmethod
    def get_bboxes(self, frame, frame_num) -> List[Bbox]:
        pass

    def _edit_frame(self, frame, frame_num):
        for bbox in self.get_bboxes(frame, frame_num):
            draw_rectangle(
                frame,
                x=bbox.x1,
                y=bbox.y1,
                w=bbox.width,
                h=bbox.height,
                color=self._bbox_color,
                thickness=self._thickness,
            )
            if self._show_above_bbox_label:
                draw_label(
                    image=frame,
                    x=bbox.x1,
                    y=bbox.y1,
                    h=bbox.height,
                    below_or_above="above",
                    text=bbox.above_label,
                    font_scale=self._font_scale,
                    thickness=self._thickness,
                    label_line_color=self._label_line_color,
                    text_color=self._label_text_color,
                    filling_color=(0, 0, 0),
                )
            if self._show_below_bbox_label:
                draw_label(
                    image=frame,
                    x=bbox.x1,
                    y=bbox.y1,
                    h=bbox.height,
                    below_or_above="below",
                    text=bbox.below_label,
                    font_scale=self._font_scale,
                    thickness=self._thickness,
                    label_line_color=self._label_line_color,
                    text_color=self._label_text_color,
                    filling_color=(0, 0, 0),
                )
        return frame

    def toggle_show_above_bbox_label(self):
        self._show_above_bbox_label = not self._show_above_bbox_label

    def toggle_show_below_bbox_label(self):
        self._show_below_bbox_label = not self._show_below_bbox_label
