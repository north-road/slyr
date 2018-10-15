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

    def children(self):
        res = super().children()
        if self.color:
            res.append(self.color)
        if self.outline_layer:
            res.append(self.outline_layer)
        if self.outline_symbol:
            res.append(self.outline_symbol)
        return res


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

    def children(self):
        res = super().children()
        if self.ramp:
            res.append(self.ramp)
        return res

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

    def children(self):
        res = super().children()
        if self.line:
            res.append(self.line)
        return res

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

    def children(self):
        res = super().children()
        if self.marker:
            res.append(self.marker)
        return res

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


class PictureFillSymbolLayer(FillSymbolLayer):
    """
    Picture fill symbol layer
    """

    def __init__(self):
        super().__init__()
        self.angle = 0
        self.scale_x = 1
        self.scale_y = 1
        self.offset_x = 0
        self.offset_y = 0
        self.separation_x = 0
        self.separation_y = 0

        self.picture = None

        self.color_foreground = None
        self.color_background = None
        self.color_transparent = None
        self.swap_fb_gb = False

    @staticmethod
    def guid():
        return 'd842b082-330c-11d2-9168-0000f87808ee'

    def children(self):
        res = super().children()
        if self.picture:
            res.append(self.picture)
        if self.color_foreground:
            res.append(self.color_foreground)
        if self.color_background:
            res.append(self.color_background)
        if self.color_transparent:
            res.append(self.color_transparent)
        return res

    @staticmethod
    def compatible_versions():
        return [4, 7, 8]

    def read(self, stream: Stream, version):
        if version == 4:
            self.picture = stream.read_object('picture')
        elif version == 7:
            _ = stream.read_ushort('pic version?')
            _ = stream.read_uint('picture type?')
            self.picture = stream.read_object('picture')
        elif version == 8:
            self.picture = stream.read_picture('picture')

        self.color_background = stream.read_object('color bg')
        self.color_foreground = stream.read_object('color fg')
        self.color_transparent = stream.read_object('color trans')

        # either an entire LineSymbol or just a LineSymbolLayer
        outline = stream.read_object('outline')
        if outline is not None:
            if issubclass(outline.__class__, SymbolLayer):
                self.outline_layer = outline
            else:
                self.outline_symbol = outline

        self.angle = stream.read_double('angle')
        self.scale_x = stream.read_double('scale_x')
        self.scale_y = stream.read_double('scale_y')

        self.offset_x = stream.read_double('offset x')
        self.offset_y = stream.read_double('offset y')
        self.separation_x = stream.read_double('separation x')
        self.separation_y = stream.read_double('separation y')

        stream.read(16)

        stream.read_0d_terminator()

        self.swap_fb_gb = bool(stream.read_uchar('swap fgbg'))

        if version <= 4:
            return

        stream.read(6)
        if version < 8:
            stream.read(4)
