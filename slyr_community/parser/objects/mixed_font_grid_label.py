#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class MixedFontGridLabel(Object):
    """
    MixedFontGridLabel
    """

    @staticmethod
    def cls_id():
        return "ce41c508-9df9-11d2-aade-000000000"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.text_symbol = None
        self.secondary_text_symbol = None
        self.number_format = None
        self.label_offset = 0

        self.top_align_hoz = False
        self.bottom_align_hoz = False
        self.left_align_hoz = False
        self.right_align_hoz = False
        self.number_grouped_digits = 0

    @staticmethod
    def compatible_versions():
        return [3]

    def read(self, stream: Stream, version):
        self.text_symbol = stream.read_object("text symbol")
        self.number_format = stream.read_object("number format")

        self.label_offset = stream.read_double("label offset")
        self.secondary_text_symbol = stream.read_object("secondary text symbol")

        stream.read_ushort("unknown")
        self.top_align_hoz = stream.read_ushort("top align hoz") != 0
        self.bottom_align_hoz = stream.read_ushort("bottom align hoz") != 0
        self.left_align_hoz = stream.read_ushort("left align hoz") != 0
        self.right_align_hoz = stream.read_ushort("right align hoz") != 0

        self.number_grouped_digits = stream.read_ushort("number ground digits")

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "text_symbol": self.text_symbol.to_dict() if self.text_symbol else None,
            "secondary_text_symbol": self.secondary_text_symbol.to_dict()
            if self.secondary_text_symbol
            else None,
            "number_format": self.number_format.to_dict()
            if self.number_format
            else None,
            "label_offset": self.label_offset,
            "top_align_hoz": self.top_align_hoz,
            "left_align_hoz": self.left_align_hoz,
            "right_align_hoz": self.right_align_hoz,
            "bottom_align_hoz": self.bottom_align_hoz,
            "number_grouped_digits": self.number_grouped_digits,
        }
