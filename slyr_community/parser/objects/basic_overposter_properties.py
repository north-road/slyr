#!/usr/bin/env python
"""
Serializable object subclass

COMPLETE INTERPRETATION
"""

from ..object import Object
from ..stream import Stream


class BasicOverposterProperties(Object):
    """
    BasicOverposterProperties
    """

    @staticmethod
    def cls_id():
        return "e0c73d56-6c88-498c-b77c-78606e688c97"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.view_unplaced = False
        self.unplaced_label_color = None
        self.rotate_point_line_labels_when_frame_rotated = False
        self.orientation_vertical_labels = 2.0

    @staticmethod
    def compatible_versions():
        return [2]

    def read(self, stream: Stream, version):
        self.view_unplaced = stream.read_ushort("view unplaced") != 0
        self.unplaced_label_color = stream.read_object("unplaced label color")
        self.rotate_point_line_labels_when_frame_rotated = (
            stream.read_ushort("rotate point/line labels when frame rotated") != 0
        )
        self.orientation_vertical_labels = stream.read_double(
            "orientation for vertical labels"
        )

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "view_unplaced": self.view_unplaced,
            "unplaced_label_color": self.unplaced_label_color.to_dict()
            if self.unplaced_label_color
            else None,
            "rotate_point_line_labels_when_frame_rotated": self.rotate_point_line_labels_when_frame_rotated,
            "orientation_vertical_labels": self.orientation_vertical_labels,
        }
