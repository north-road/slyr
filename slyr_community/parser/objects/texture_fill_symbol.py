#!/usr/bin/env python
"""
Serializable object subclass
"""

from slyr_community.parser.objects.symbol_layer import SymbolLayer
from slyr_community.parser.stream import Stream


class TextureFillSymbol(SymbolLayer):
    """
    TextureFillSymbol
    """

    @staticmethod
    def cls_id():
        return '8d738780-c069-42e0-9dfa-2b7b61707ba9'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.texture = None
        self.color = None
        self.transparency_color = None
        self.outline = None
        self.angle = 0
        self.size = 0
        self.symbol_level = 0

    @staticmethod
    def compatible_versions():
        return [2]

    def read(self, stream: Stream, version):
        self.texture = stream.read_object('texture')
        self.color = stream.read_object('color')
        self.transparency_color = stream.read_object('transparency color')
        self.outline = stream.read_object('outline')
        self.angle = stream.read_double('angle')
        self.size = stream.read_double('size')

        stream.read_int('raster op', expected=13)
        self.symbol_level = stream.read_int('level')

    def to_dict(self):
        return {
            'texture': self.texture.to_dict() if self.texture else None,
            'color': self.color.to_dict() if self.color else None,
            'transparency_color': self.transparency_color.to_dict() if self.transparency_color else None,
            'outline': self.outline.to_dict() if self.outline else None,
            'angle': self.angle,
            'size': self.size,
            'symbol_level': self.symbol_level,
        }
