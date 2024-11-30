from abc import ABC, abstractmethod
from typing import Tuple, List

from ..frame_editors import BaseFrameEditCallback
from ..utils.bbox_utils import Bbox, BboxFormat
from ..utils.drawing_utils import draw_rectangle, draw_label
from ..utils.video_player_utils import KeyFunction


class BaseBboxPlotter(BaseFrameEditCallback, ABC):
    """
    An abstract class that can be used a parent to any FrameEditor that needs to print bounding boxes on the frame.
    The self._edit_frame is already implemented and instead the derived class must implement the "get_bboxes" method.
    """

    def __init__(
        self,
        enable_by_default: bool = False,
        enable_disable_key: str = None,
        show_above_bbox_label: bool = True,
        show_below_bbox_label: bool = True,
        default_bbox_color: Tuple[int, int, int] = (255, 0, 0),
        text_color: Tuple[int, int, int] = (255, 255, 255),
        drawing_thickness: int = 1,
        font_scale: float = 2.0,
        label_text_color: Tuple[int, int, int] = (255, 255, 255),
        label_filling_color: Tuple[int, int, int] = (0, 0, 0),
    ):
        super().__init__(enable_by_default, enable_disable_key)
        self._text_color = text_color
        self._font_scale = font_scale
        self._thickness = drawing_thickness
        self._show_above_bbox_label = show_above_bbox_label
        self._show_below_bbox_label = show_below_bbox_label
        self._default_bbox_color = default_bbox_color
        self._label_text_color = label_text_color
        self._label_filling_color = label_filling_color

    @abstractmethod
    def get_bboxes(self, edited_frame, original_frame, frame_num) -> List[Bbox]:
        pass

    @property
    def key_function_to_register(self):
        return super().key_function_to_register + [
            KeyFunction(key="l", func=self._toggle_show_above_bbox_label, description="Show/Hide above label"),
            KeyFunction(key="b", func=self._toggle_show_below_bbox_label, description="Show/Hide below label"),
            KeyFunction(key="ctrl+i", func=lambda: self._change_font_size(0.1), description="increase label size"),
            KeyFunction(key="ctrl+u", func=lambda: self._change_font_size(-0.1), description="decrease label size"),
        ]

    def edit_frame(self, frame, frame_num, original_frame, **kwargs):
        for bbox in self.get_bboxes(
                edited_frame=frame,
                original_frame=original_frame,
                frame_num=frame_num,
        ):
            norm_bbox = bbox.get_normalized_bbox(
                frame_width=original_frame.shape[1],
                frame_height=original_frame.shape[0],
                bbox_format=BboxFormat.xywh,
            )

            resized_bbox_coords = (
                int(norm_bbox[0] * frame.shape[1]),
                int(norm_bbox[1] * frame.shape[0]),
                int(norm_bbox[2] * frame.shape[1]),
                int(norm_bbox[3] * frame.shape[0]),
            )

            draw_rectangle(
                frame,
                x=resized_bbox_coords[0],
                y=resized_bbox_coords[1],
                w=resized_bbox_coords[2],
                h=resized_bbox_coords[3],
                color=bbox.color or self._default_bbox_color,
                thickness=self._thickness,
            )
            if self._show_above_bbox_label and bbox.above_label is not None:
                draw_label(
                    frame=frame,
                    bbox_x1=resized_bbox_coords[0],
                    bbox_y1=resized_bbox_coords[1],
                    bbox_h=resized_bbox_coords[3],
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
                    bbox_x1=resized_bbox_coords[0],
                    bbox_y1=resized_bbox_coords[1],
                    bbox_h=resized_bbox_coords[3],
                    below_or_above="below",
                    text=bbox.below_label,
                    font_scale=self._font_scale,
                    thickness=self._thickness,
                    label_line_color=bbox.color or self._default_bbox_color,
                    text_color=self._label_text_color,
                    filling_color=self._label_filling_color,
                )
        return frame

    def _toggle_show_above_bbox_label(self):
        self._show_above_bbox_label = not self._show_above_bbox_label

    def _toggle_show_below_bbox_label(self):
        self._show_below_bbox_label = not self._show_below_bbox_label

    def _change_font_size(self, by: float):
        self._font_scale = max(0.1, min(5.0, self._font_scale + by))
