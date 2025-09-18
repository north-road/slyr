#!/usr/bin/env python
"""
Serializable object subclass

COMPLETE INTERPRETATION
"""

from ..object import Object
from ..stream import Stream
from .arcobjects_enums import DMSGridLabelType


class DMSGridLabel(Object):
    """
    DMSGridLabel
    """

    @staticmethod
    def cls_id():
        return "ce41c506-9df9-11d2-aade-000000000"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.label_type: DMSGridLabelType = DMSGridLabelType.Standard
        self.text_symbol = None
        self.minutes_text_symbol = None
        self.seconds_text_symbol = None
        self.number_format = None
        self.label_offset = 0
        self.top_align_hoz = False
        self.left_align_hoz = False
        self.right_align_hoz = False
        self.bottom_align_hoz = False
        self.abbreviated_labels = False
        self.show_zero_minutes = False
        self.show_zero_seconds = False
        self.show_minus_sign = False

    @staticmethod
    def compatible_versions():
        return [2, 3, 4]

    def read(self, stream: Stream, version):
        self.label_type = DMSGridLabelType(stream.read_int("label type"))
        self.text_symbol = stream.read_object("text symbol")
        self.minutes_text_symbol = stream.read_object("minutes text symbol")
        self.seconds_text_symbol = stream.read_object("seconds text symbol")

        self.show_zero_minutes = stream.read_ushort("show zero minutes") != 0
        self.show_zero_seconds = stream.read_ushort("show zero seconds") != 0

        self.number_format = stream.read_object("lat lon format")

        self.label_offset = stream.read_double("label offset")
        stream.read_ushort()

        self.top_align_hoz = stream.read_ushort("top align hoz") != 0
        self.bottom_align_hoz = stream.read_ushort("bottom align hoz") != 0
        self.left_align_hoz = stream.read_ushort("left align hoz") != 0
        self.right_align_hoz = stream.read_ushort("right align hoz") != 0

        if version > 2:
            self.abbreviated_labels = stream.read_ushort("abbreviated labels") != 0
        if version > 3:
            self.show_minus_sign = stream.read_ushort("show minus sign") != 0

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "label_type": str(self.label_type),
            "text_symbol": self.text_symbol.to_dict() if self.text_symbol else None,
            "minutes_text_symbol": self.minutes_text_symbol.to_dict()
            if self.minutes_text_symbol
            else None,
            "seconds_text_symbol": self.seconds_text_symbol.to_dict()
            if self.seconds_text_symbol
            else None,
            "number_format": self.number_format.to_dict()
            if self.number_format
            else None,
            "label_offset": self.label_offset,
            "top_align_hoz": self.top_align_hoz,
            "left_align_hoz": self.left_align_hoz,
            "right_align_hoz": self.right_align_hoz,
            "bottom_align_hoz": self.bottom_align_hoz,
            "abbreviated_labels": self.abbreviated_labels,
            "show_zero_minutes": self.show_zero_minutes,
            "show_zero_seconds": self.show_zero_seconds,
            "show_minus_sign": self.show_minus_sign,
        }
