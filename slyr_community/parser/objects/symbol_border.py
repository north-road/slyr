#!/usr/bin/env python
"""
SymbolBorder

COMPLETE INTERPRETATION
"""

from ..object import Object
from ..stream import Stream


class SymbolBorder(Object):
    """
    SymbolBorder
    """

    @staticmethod
    def cls_id():
        return "a5d0f017-62dd-11d2-87be-0000f8751720"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.symbol = None
        self.gap_x = 0
        self.gap_y = 0
        self.rounding = 0

    @staticmethod
    def compatible_versions():
        return [1, 2]

    def read(self, stream: Stream, version):
        self.gap_x = stream.read_double("gap x")
        self.symbol = stream.read_object("symbol")
        self.rounding = stream.read_ushort("rounding")
        if version > 1:
            self.gap_y = stream.read_double("gap y")

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "symbol": self.symbol.to_dict() if self.symbol else None,
            "gap_x": self.gap_x,
            "gap_y": self.gap_y,
            "rounding": self.rounding,
        }
