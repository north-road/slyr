#!/usr/bin/env python
"""
Serializable object subclass

NEAR COMPLETE INTERPRETATION - all useful components
"""

from ..object import Object
from ..stream import Stream


class CornerGridLabel(Object):
    """
    CornerGridLabel
    """

    @staticmethod
    def cls_id():
        return "fd52b61a-71cd-4108-a916-f818969404ea"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.grid_label_text_symbol = None
        self.small_label_text_symbol = None
        self.principal_digit_count = 0
        self.base_digit_count = 0
        self.corner_label_lower_left = False
        self.corner_label_lower_right = False
        self.corner_label_upper_left = False
        self.corner_label_upper_right = False
        self.unit_suffix = ""
        self.easting_suffix = ""
        self.northing_suffix = ""
        self.number_format = None
        self.label_offset = 0
        self.top_align_hoz = False
        self.bottom_align_hoz = False
        self.left_align_hoz = False
        self.right_align_hoz = False

    @staticmethod
    def compatible_versions():
        return [2]

    def read(self, stream: Stream, version):
        self.grid_label_text_symbol = stream.read_object("grid label text symbol")

        self.number_format = stream.read_object("number format")
        self.label_offset = stream.read_double("label offset")

        self.small_label_text_symbol = stream.read_object("small label text symbol")

        stream.read_ushort("unknown")

        self.top_align_hoz = stream.read_ushort("top align hoz") != 0
        self.bottom_align_hoz = stream.read_ushort("bottom align hoz") != 0
        self.left_align_hoz = stream.read_ushort("left align hoz") != 0
        self.right_align_hoz = stream.read_ushort("right align hoz") != 0

        self.corner_label_lower_left = (
            stream.read_ushort("corner label lower left") != 0
        )
        self.corner_label_lower_right = (
            stream.read_ushort("corner label lower right") != 0
        )
        self.corner_label_upper_left = (
            stream.read_ushort("corner label upper left") != 0
        )
        self.corner_label_upper_right = (
            stream.read_ushort("corner label upper right") != 0
        )
        self.principal_digit_count = stream.read_int("principal digit count")
        self.base_digit_count = stream.read_int("base digit count")

        self.unit_suffix = stream.read_string("unit suffix")
        self.easting_suffix = stream.read_string("easting suffix")
        self.northing_suffix = stream.read_string("northing suffix")

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "grid_label_text_symbol": self.grid_label_text_symbol.to_dict()
            if self.grid_label_text_symbol
            else None,
            "small_label_text_symbol": self.small_label_text_symbol.to_dict()
            if self.small_label_text_symbol
            else None,
            "principal_digit_count": self.principal_digit_count,
            "base_digit_count": self.base_digit_count,
            "corner_label_lower_left": self.corner_label_lower_left,
            "corner_label_lower_right": self.corner_label_lower_right,
            "corner_label_upper_left": self.corner_label_upper_left,
            "corner_label_upper_right": self.corner_label_upper_right,
            "unit_suffix": self.unit_suffix,
            "easting_suffix": self.easting_suffix,
            "northing_suffix": self.northing_suffix,
            "label_offset": self.label_offset,
            "number_format": self.number_format.to_dict()
            if self.number_format
            else None,
            "top_align_hoz": self.top_align_hoz,
            "left_align_hoz": self.left_align_hoz,
            "right_align_hoz": self.right_align_hoz,
            "bottom_align_hoz": self.bottom_align_hoz,
        }
