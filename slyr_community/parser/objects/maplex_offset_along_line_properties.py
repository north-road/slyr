#!/usr/bin/env python
"""
Serializable object subclass

"""

from ..object import Object
from ..stream import Stream
from .maplex_utils import MaplexUtils


class MaplexOffsetAlongLineProperties(Object):
    """
    MaplexOffsetAlongLineProperties
    """

    OFFSET_BEST_POSITION_ALONG_LINE = 0
    OFFSET_BEFORE_START_OF_LINE = 1
    OFFSET_ALONG_LINE_FROM_START = 2
    OFFSET_ALONG_LINE_FROM_END = 3
    OFFSET_AFTER_END_OF_LINE = 4

    ANCHOR_CENTER_OF_LABEL = 0
    ANCHOR_NEAREST_SIDE_OF_LABEL = 1
    ANCHOR_FURTHEST_SIDE_OF_LABEL = 2

    @staticmethod
    def cls_id():
        return "20664808-4fa1-c1d1-8c0a-08a2c9ed531a"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.placement_method = (
            MaplexOffsetAlongLineProperties.OFFSET_BEST_POSITION_ALONG_LINE
        )
        self.distance = 0
        self.tolerance = 0
        self.unit = MaplexUtils.UNIT_MAP
        self.anchor = MaplexOffsetAlongLineProperties.ANCHOR_CENTER_OF_LABEL
        self.use_line_direction = True

    @staticmethod
    def compatible_versions():
        return [2]

    @staticmethod
    def placement_method_to_string(method):
        """
        Converts a placement method to string
        """
        if method == MaplexOffsetAlongLineProperties.OFFSET_BEST_POSITION_ALONG_LINE:
            return "best_position_along_line"
        elif method == MaplexOffsetAlongLineProperties.OFFSET_BEFORE_START_OF_LINE:
            return "before_start_of_line"
        elif method == MaplexOffsetAlongLineProperties.OFFSET_ALONG_LINE_FROM_START:
            return "along_line_from_start"
        elif method == MaplexOffsetAlongLineProperties.OFFSET_ALONG_LINE_FROM_END:
            return "along_line_from_end"
        elif method == MaplexOffsetAlongLineProperties.OFFSET_AFTER_END_OF_LINE:
            return "after_end_of_line"
        return None

    @staticmethod
    def anchor_to_string(anchor):
        """
        Converts and anchor type to string
        """
        if anchor == MaplexOffsetAlongLineProperties.ANCHOR_CENTER_OF_LABEL:
            return "center_of_label"
        elif anchor == MaplexOffsetAlongLineProperties.ANCHOR_NEAREST_SIDE_OF_LABEL:
            return "nearest_side_of_label"
        elif anchor == MaplexOffsetAlongLineProperties.ANCHOR_FURTHEST_SIDE_OF_LABEL:
            return "furthest_side_of_label"
        return None

    def read(self, stream: Stream, version):
        self.placement_method = stream.read_int("method")
        self.anchor = stream.read_int("anchor")
        self.distance = stream.read_double("distance percent")
        self.tolerance = stream.read_double("tolerance percent")
        self.unit = stream.read_int("unit")
        self.use_line_direction = stream.read_ushort("use line direction") != 0

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "placement_method": MaplexOffsetAlongLineProperties.placement_method_to_string(
                self.placement_method
            ),
            "distance": self.distance,
            "tolerance": self.tolerance,
            "unit": MaplexUtils.unit_to_string(self.unit),
            "anchor": MaplexOffsetAlongLineProperties.anchor_to_string(self.anchor),
            "use_line_direction": self.use_line_direction,
        }
