"""
This module contains an drawing routines based on OpenCV.
"""

import cv2
import numpy as np


def draw_rectangle(
    image,
    x,
    y,
    w,
    h,
    color,
    thickness=2,
):
    """Draw a rectangle."""
    pt1 = int(x), int(y)
    pt2 = int(x + w), int(y + h)
    cv2.rectangle(image, pt1, pt2, color, thickness, lineType=cv2.LINE_AA)


def draw_polygon(
    image,
    points,
    color,
    thickness=2,
):
    """Draw a rectangle."""
    points = np.array(points).reshape((-1, 1, 2)).astype(np.int32)
    cv2.polylines(image, [points], isClosed=True, color=color, thickness=thickness, lineType=cv2.LINE_AA)


def draw_label(
    x,
    y,
    h,
    below_or_above,
    image,
    text,
    font_scale,
    thickness,
    label_line_color,
    text_color,
    filling_color=(0, 0, 0),
):
    assert below_or_above in {"below", "above"}
    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_PLAIN, fontScale=font_scale, thickness=thickness)

    label_pt1 = int(x), int(y - 10 - text_size[0][1])
    label_pt2 = int(x + 10 + text_size[0][0]), int(y)
    up_left = label_pt1[0] + 5, label_pt2[1] + 5 + h + text_size[0][1]
    bottom_left = label_pt1[0] + 5, label_pt2[1] - 5

    position = up_left if below_or_above == "below" else bottom_left

    if below_or_above == "above":
        cv2.rectangle(image, label_pt1, label_pt2, color=filling_color, thickness=-1, lineType=cv2.LINE_AA)
        cv2.rectangle(image, label_pt1, label_pt2, color=label_line_color, thickness=thickness, lineType=cv2.LINE_AA)

    cv2.putText(
        img=image,
        text=text,
        org=position,
        fontFace=cv2.FONT_HERSHEY_PLAIN,
        fontScale=font_scale,
        color=text_color,
        thickness=thickness,
        lineType=cv2.LINE_AA,
    )
