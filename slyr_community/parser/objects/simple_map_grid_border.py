#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class SimpleMapGridBorder(Object):
    """
    SimpleMapGridBorder
    """

    @staticmethod
    def cls_id():
        return "ac81ecfb-9ee4-11d2-aadf-000000000"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.line_symbol = None

    def read(self, stream: Stream, version):
        self.line_symbol = stream.read_object("line symbol")

    def to_dict(self):  # pylint: disable=method-hidden
        return {"line_symbol": self.line_symbol.to_dict() if self.line_symbol else None}
