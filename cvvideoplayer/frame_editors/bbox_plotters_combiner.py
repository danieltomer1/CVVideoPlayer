from typing import List

from ..utils.bbox_utils import Bbox
from ..frame_editors import BaseBboxPlotter


class BboxPlottersCombiner(BaseBboxPlotter):
    def __init__(
        self,
        bbox_plotters: List[BaseBboxPlotter],
        **bboxes_plotter_kwargs,
    ):
        super().__init__(enable_by_default=True, **bboxes_plotter_kwargs)
        self._bbox_plotters = bbox_plotters

    def setup(self, **kwargs) -> None:
        for bbox_plotter in self._bbox_plotters:
            bbox_plotter.setup(**kwargs)

    @property
    def key_function_to_register(self):
        combined_key_dict = {}
        for bbox_plotter in self._bbox_plotters:
            combined_key_dict.update(
                {key_function.key: key_function for key_function in bbox_plotter.key_function_to_register})

        combined_key_dict.update(
            {key_function.key: key_function for key_function in super().key_function_to_register})

        return list(combined_key_dict.values())

    def edit_frame(self, frame, frame_num, original_frame, **kwargs):
        frame = super().edit_frame(frame=frame, original_frame=original_frame, frame_num=frame_num, **kwargs)
        return frame

    def get_bboxes(self, original_frame, frame_num, **kwargs) -> List[Bbox]:
        bboxes = []
        for bbox_plotter in self._bbox_plotters:
            if not bbox_plotter.enabled:
                continue
            bboxes.extend(bbox_plotter.get_bboxes(
                original_frame=original_frame,
                frame_num=frame_num,
                **kwargs
            ))
        return bboxes

    def teardown(self):
        for bbox_plotter in self._bbox_plotters:
            bbox_plotter.teardown()
