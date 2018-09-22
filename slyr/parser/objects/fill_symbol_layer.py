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

    def _read(self, stream: Stream):
        # first bit is either an entire LineSymbol or just a LineSymbolLayer
        outline = stream.read_object('outline')
        if outline is not None:
            if issubclass(outline.__class__, SymbolLayer):
                self.outline_layer = outline
            else:
                self.outline_symbol = outline

        self.color = stream.read_object('color')
