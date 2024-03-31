from abc import ABC, abstractmethod
from typing import *

from cvvideoplayer.frame_editors import BaseFrameEditor
from cvvideoplayer.utils.bbox_utils import Bbox
from cvvideoplayer.utils.drawing_utils import draw_rectangle, draw_label
from cvvideoplayer.utils.video_player_utils import KeymapAction


class BaseBboxPlotter(BaseFrameEditor, ABC):
    def __init__(
        self,
        enable_by_default: bool = False,
        show_above_bbox_label: bool = True,
        show_below_bbox_label: bool = True,
        default_bbox_color: Tuple[int, int, int] = (255, 0, 0),
        text_color: Tuple[int, int, int] = (255, 255, 255),
        drawing_thickness: int = 1,
        font_scale: float = 0.5,
        label_text_color: Tuple[int, int, int] = (255, 255, 255),
        label_filling_color: Tuple[int, int, int] = (0, 0, 0),
    ):
        super().__init__(enable_by_default)
        self._text_color = text_color
        self._font_scale = font_scale
        self._thickness = drawing_thickness
        self._show_above_bbox_label = show_above_bbox_label
        self._show_below_bbox_label = show_below_bbox_label
        self._default_bbox_color = default_bbox_color
        self._label_text_color = label_text_color
        self._label_filling_color = label_filling_color

    @abstractmethod
    def get_bboxes(self, frame, frame_num) -> List[Bbox]:
        pass

    @property
    def edit_after_resize(self) -> bool:
        return False

    @property
    def keymap_actions_to_register(self):
        return {
            "d": KeymapAction(self.enable_disable, "Show/Hide Detections"),
            "l": KeymapAction(self.toggle_show_above_bbox_label, "Show/Hide above label"),
            "b": KeymapAction(self.toggle_show_below_bbox_label, "Show/Hide below label"),
        }

    def _edit_frame(self, frame, frame_num):
        for bbox in self.get_bboxes(frame, frame_num):
            draw_rectangle(
                frame,
                x=bbox.x1,
                y=bbox.y1,
                w=bbox.width,
                h=bbox.height,
                color=bbox.color or self._default_bbox_color,
                thickness=self._thickness,
            )
            if self._show_above_bbox_label and bbox.above_label is not None:
                draw_label(
                    frame=frame,
                    bbox_x1=bbox.x1,
                    bbox_y1=bbox.y1,
                    bbox_h=bbox.height,
                    below_or_above="above",
                    text=bbox.above_label,
                    font_scale=self._font_scale,
                    thickness=self._thickness,
                    label_line_color=bbox.color or self._default_bbox_color,
                    text_color=self._label_text_color,
                    filling_color=self._label_filling_color,
                )
            if self._show_below_bbox_label and bbox.below_label is not None:
                draw_label(
                    frame=frame,
                    bbox_x1=bbox.x1,
                    bbox_y1=bbox.y1,
                    bbox_h=bbox.height,
                    below_or_above="below",
                    text=bbox.below_label,
                    font_scale=self._font_scale,
                    thickness=self._thickness,
                    label_line_color=bbox.color or self._default_bbox_color,
                    text_color=self._label_text_color,
                    filling_color=self._label_filling_color,
                )
        return frame

    def toggle_show_above_bbox_label(self):
        self._show_above_bbox_label = not self._show_above_bbox_label

    def toggle_show_below_bbox_label(self):
        self._show_below_bbox_label = not self._show_below_bbox_label
