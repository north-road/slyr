#!/usr/bin/env python
"""
Serializable object subclass
"""

from .symbol_layer import SymbolLayer
from ..stream import Stream


class TextureLineSymbol(SymbolLayer):
    """
    TextureLineSymbol
    """

    @staticmethod
    def cls_id():
        return 'b5710c9c-a9bc-4a16-b578-54be176ed57b'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.texture_fill_symbol = None
        self.vertical_orientation = False
        self.width = 0

    @staticmethod
    def compatible_versions():
        return [2]

    def read(self, stream: Stream, version):
        self.width = stream.read_double('width')
        self.texture_fill_symbol = stream.read_object('texture fill symbol')
        self.vertical_orientation = stream.read_uchar('vertical orientation') != 0

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'texture_fill_symbol': self.texture_fill_symbol.to_dict() if self.texture_fill_symbol else None,
            'vertical_orientation': self.vertical_orientation,
            'width': self.width
        }
