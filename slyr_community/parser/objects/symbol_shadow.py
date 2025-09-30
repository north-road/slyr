#!/usr/bin/env python
"""
Serializable object subclass

COMPLETE INTERPRETATION
"""

from ..object import Object
from ..stream import Stream


class SymbolShadow(Object):
    """
    SymbolShadow
    """

    @staticmethod
    def cls_id():
        return "a8861e66-57aa-47d0-aaf8-b288b4fd5240"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.symbol = None
        self.rounding = 0
        self.x_offset = 0
        self.y_offset = 0

    def read(self, stream: Stream, version):
        self.symbol = stream.read_object("symbol")
        self.rounding = stream.read_ushort("rounding")
        self.x_offset = stream.read_double("x offset")
        self.y_offset = stream.read_double("y offset")

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "symbol": self.symbol.to_dict() if self.symbol else None,
            "offset_x": self.x_offset,
            "offset_y": self.y_offset,
            "rounding": self.rounding,
        }
