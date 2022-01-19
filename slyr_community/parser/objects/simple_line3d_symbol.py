#!/usr/bin/env python
"""
Serializable object subclass
"""

from typing import Optional
from .symbol_layer import SymbolLayer
from ..stream import Stream


class SimpleLine3DSymbol(SymbolLayer):
    """
    SimpleLine3DSymbol
    """

    TUBE = 0
    STRIP = 1
    WALL = 2

    @staticmethod
    def cls_id():
        return '470b7275-3552-11d6-a12d-00508bd60cb9'

    @staticmethod
    def type_to_string(line_type) -> Optional[str]:
        """
        Converts a line type to a string representation
        """

        if line_type == SimpleLine3DSymbol.TUBE:
            return 'tube'
        elif line_type == SimpleLine3DSymbol.STRIP:
            return 'strip'
        elif line_type == SimpleLine3DSymbol.WALL:
            return 'wall'
        return None

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.color = None
        self.width = 1
        self.quality = 0.5
        self.type = SimpleLine3DSymbol.TUBE

    def read(self, stream: Stream, version):
        self.color = stream.read_object('color')
        self.width = stream.read_double('width')
        self.type = stream.read_int('type', expected=(0, 1, 2))
        self.quality = stream.read_double('quality')

        self.symbol_level = SymbolLayer.read_symbol_level(stream)

    def to_dict(self):  # pylint: disable=method-hidden
        out = {
            'color': self.color.to_dict() if self.color is not None else None,
            'width': self.width,
            'quality': self.quality,
            'line_type': SimpleLine3DSymbol.type_to_string(self.type)
        }
        return out
