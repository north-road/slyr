#!/usr/bin/env python
"""
SymbolBackground

COMPLETE INTERPRETATION

"""

from ..object import Object
from ..stream import Stream


class SymbolBackground(Object):
    """
    SymbolBackground
    """

    @staticmethod
    def cls_id():
        return "1baa33e9-e13b-11d2-b868-00600802e603"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.symbol = None
        self.gap_x = 0
        self.gap_y = 0
        self.rounding = 0

    @staticmethod
    def compatible_versions():
        return [2]

    def read(self, stream: Stream, version):
        self.gap_x = stream.read_double("gap x")
        self.symbol = stream.read_object("symbol")
        self.rounding = stream.read_ushort("rounding")
        self.gap_y = stream.read_double("gap y")

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "symbol": self.symbol.to_dict() if self.symbol else None,
            "gap_x": self.gap_x,
            "gap_y": self.gap_y,
            "rounding": self.rounding,
        }
