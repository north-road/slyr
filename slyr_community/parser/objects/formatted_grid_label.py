#!/usr/bin/env python
"""
Serializable object subclass

NEAR COMPLETE INTERPRETATION - all useful components
"""

from ..object import Object
from ..stream import Stream


class FormattedGridLabel(Object):
    """
    FormattedGridLabel
    """

    @staticmethod
    def cls_id():
        return "ce41c507-9df9-11d2-aade-000000000"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.text_symbol = None
        self.label_offset = 0
        self.top_align_hoz = False
        self.bottom_align_hoz = False
        self.left_align_hoz = False
        self.right_align_hoz = False
        self.number_format = None

    @staticmethod
    def compatible_versions():
        return [2]

    def read(self, stream: Stream, version):
        self.text_symbol = stream.read_object("text symbol")
        self.number_format = stream.read_object("number format")
        self.label_offset = stream.read_double("label offset")

        stream.read_ushort("unknown")

        self.top_align_hoz = stream.read_ushort("top align hoz") != 0
        self.bottom_align_hoz = stream.read_ushort("bottom align hoz") != 0
        self.left_align_hoz = stream.read_ushort("left align hoz") != 0
        self.right_align_hoz = stream.read_ushort("right align hoz") != 0

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "text_symbol": self.text_symbol.to_dict() if self.text_symbol else None,
            "number_format": self.number_format.to_dict()
            if self.number_format
            else None,
            "label_offset": self.label_offset,
            "top_align_hoz": self.top_align_hoz,
            "left_align_hoz": self.left_align_hoz,
            "right_align_hoz": self.right_align_hoz,
            "bottom_align_hoz": self.bottom_align_hoz,
        }
