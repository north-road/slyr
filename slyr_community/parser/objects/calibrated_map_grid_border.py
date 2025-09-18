#!/usr/bin/env python
"""
Serializable object subclass

COMPLETE INTERPRETATION
"""

from ..object import Object
from ..stream import Stream


class CalibratedMapGridBorder(Object):
    """
    CalibratedMapGridBorder
    """

    @staticmethod
    def cls_id():
        return "6ca416b0-e160-11d2-9f4e-00c04f6bc78e"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.foreground_symbol = None
        self.background_symbol = None
        self.border_width = 1
        self.interval = 1
        self.alternating = False

    def read(self, stream: Stream, version):
        self.foreground_symbol = stream.read_object("foreground symbol")
        self.background_symbol = stream.read_object("background symbol")
        self.border_width = stream.read_double("border width")
        self.interval = stream.read_double("interval")
        self.alternating = stream.read_ushort("alternating") != 0

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "foreground_symbol": self.foreground_symbol.to_dict()
            if self.foreground_symbol
            else None,
            "background_symbol": self.background_symbol.to_dict()
            if self.background_symbol
            else None,
            "border_width": self.border_width,
            "interval": self.interval,
            "alternating": self.alternating,
        }
