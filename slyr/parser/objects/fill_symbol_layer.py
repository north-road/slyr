#!/usr/bin/env python
"""
Fill symbol layers
"""

from slyr.parser.objects.symbol_layer import SymbolLayer
from slyr.parser.stream import Stream


class FillSymbolLayer(SymbolLayer):
    """
    Base class for fill symbol layers
    """

    def __init__(self):
        super().__init__()
        self.color = None
        self.outline_layer = None
        self.outline_symbol = None


class SimpleFillSymbolLayer(FillSymbolLayer):
    """
    Simple fill symbol layer
    """

    @staticmethod
    def guid():
        return '7914e603-c892-11d0-8bb6-080009ee4e41'

    def read(self, stream: Stream, version):
        # first bit is either an entire LineSymbol or just a LineSymbolLayer
        outline = stream.read_object('outline')
        if outline is not None:
            if issubclass(outline.__class__, SymbolLayer):
                self.outline_layer = outline
            else:
                self.outline_symbol = outline

        self.color = stream.read_object('color')
        stream.read_0d_terminator()
        _ = stream.read_int('unknown int')


class ColorSymbol(FillSymbolLayer):
    """
    Officially 'ColorSymbol for raster rendering' -- but sometimes found in fill symbols!
    """

    @staticmethod
    def guid():
        return 'b81f9ae0-026e-11d3-9c1f-00c04f5aa6ed'

    def read(self, stream: Stream, version):
        self.color = stream.read_object('color')
        stream.read_0d_terminator()
