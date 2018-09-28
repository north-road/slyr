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


class GradientFillSymbolLayer(FillSymbolLayer):
    """
    Gradient fill symbol layer
    """

    LINEAR = 0
    RECTANGULAR = 1
    CIRCULAR = 2
    BUFFERED = 3

    def __init__(self):
        super().__init__()
        self.ramp = None
        self.type = None
        self.percent = 0
        self.intervals = 5
        self.angle = 0

    @staticmethod
    def guid():
        return '7914e609-c892-11d0-8bb6-080009ee4e41'

    def read(self, stream: Stream, version):
        self.ramp = stream.read_object('Color ramp')
        _ = stream.read_object('unused color')

        # either an entire LineSymbol or just a LineSymbolLayer
        outline = stream.read_object('outline')
        if outline is not None:
            if issubclass(outline.__class__, SymbolLayer):
                self.outline_layer = outline
            else:
                self.outline_symbol = outline

        self.percent = stream.read_double('percent')
        self.intervals = stream.read_uint('intervals')
        self.angle = stream.read_double('angle')

        self.type = stream.read_uint('Gradient type')
        stream.read_0d_terminator()


class LineFillSymbolLayer(FillSymbolLayer):
    """
    Line fill symbol layer
    """

    def __init__(self):
        super().__init__()
        self.angle = 0
        self.offset = 0
        self.separation = 0
        self.line = None

    @staticmethod
    def guid():
        return '7914e606-c892-11d0-8bb6-080009ee4e41'

    def read(self, stream: Stream, version):
        _ = stream.read_double('unused double')
        _ = stream.read_double('unused double')

        self.line = stream.read_object('pattern line')

        # either an entire LineSymbol or just a LineSymbolLayer
        outline = stream.read_object('outline')
        if outline is not None:
            if issubclass(outline.__class__, SymbolLayer):
                self.outline_layer = outline
            else:
                self.outline_symbol = outline

        self.angle = stream.read_double('angle')
        self.offset = stream.read_double('offset')
        self.separation = stream.read_double('separation')

        stream.read_0d_terminator()


class MarkerFillSymbolLayer(FillSymbolLayer):
    """
    Marker fill symbol layer
    """

    def __init__(self):
        super().__init__()
        self.random = False
        self.offset_x = 0
        self.offset_y = 0
        self.separation_x = 0
        self.separation_y = 0
        self.marker = None

    @staticmethod
    def guid():
        return '7914e608-c892-11d0-8bb6-080009ee4e41'

    def read(self, stream: Stream, version):
        self.random = bool(stream.read_int('random'))
        self.offset_x = stream.read_double('offset x')
        self.offset_y = stream.read_double('offset y')
        self.separation_x = stream.read_double('separation x')
        self.separation_y = stream.read_double('separation y')
        _ = stream.read_double('unused double')
        _ = stream.read_double('unused double')

        self.marker = stream.read_object('fill marker')

        # either an entire LineSymbol or just a LineSymbolLayer
        outline = stream.read_object('outline')
        if outline is not None:
            if issubclass(outline.__class__, SymbolLayer):
                self.outline_layer = outline
            else:
                self.outline_symbol = outline

        stream.read_0d_terminator()

        _ = stream.read_double('unused double')
