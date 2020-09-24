#!/usr/bin/env python
"""
Fill symbol layers

COMPLETE INTERPRETATION of common subclasses
"""

from slyr_community.parser.objects.symbol_layer import SymbolLayer
from slyr_community.parser.stream import Stream
from slyr_community.parser.exceptions import NotImplementedException
from slyr_community.parser.objects.picture import Picture


class FillSymbolLayer(SymbolLayer):
    """
    Base class for fill symbol layers
    """

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.color = None
        self.outline = None

    def children(self):
        res = super().children()
        if self.color:
            res.append(self.color)
        if self.outline:
            res.append(self.outline)
        return res


class SimpleFillSymbol(FillSymbolLayer):
    """
    Simple fill symbol layer
    """

    STYLE_SOLID = 0
    STYLE_NULL = 1
    STYLE_HORIZONTAL = 2
    STYLE_VERTICAL = 3
    STYLE_FORWARD_DIAGONAL = 4
    STYLE_BACKWARD_DIAGONAL = 5
    STYLE_CROSS = 6
    STYLE_DIAGONAL_CROSS = 7

    @staticmethod
    def cls_id():
        return '7914e603-c892-11d0-8bb6-080009ee4e41'

    @staticmethod
    def fill_style_to_string(style):
        """
        Converts a fill style value to a string representation
        """
        style_map = {
            SimpleFillSymbol.STYLE_SOLID: 'solid',
            SimpleFillSymbol.STYLE_NULL: 'null',
            SimpleFillSymbol.STYLE_HORIZONTAL: 'horizontal',
            SimpleFillSymbol.STYLE_VERTICAL: 'vertical',
            SimpleFillSymbol.STYLE_FORWARD_DIAGONAL: 'forward_diagonal',
            SimpleFillSymbol.STYLE_BACKWARD_DIAGONAL: 'backward_diagonal',
            SimpleFillSymbol.STYLE_CROSS: 'cross',
            SimpleFillSymbol.STYLE_DIAGONAL_CROSS: 'diagonal_cross',
        }
        assert style in style_map
        return style_map[style]

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.fill_style = SimpleFillSymbol.STYLE_SOLID

    def to_dict(self):  # pylint: disable=method-hidden
        out = {'color': self.color.to_dict() if self.color is not None else None}
        if self.outline:
            out['outline'] = self.outline.to_dict()
        out['fill_style'] = SimpleFillSymbol.fill_style_to_string(self.fill_style)

        return out

    def read(self, stream: Stream, version):
        # first bit is either an entire LineSymbol or just a LineSymbolLayer
        self.outline = stream.read_object('outline')
        self.color = stream.read_object('color')
        self.symbol_level = SymbolLayer.read_symbol_level(stream)
        self.fill_style = stream.read_int('fill style')


class ColorSymbol(FillSymbolLayer):
    """
    Officially 'ColorSymbol for raster rendering' -- but sometimes found in fill symbols!
    """

    @staticmethod
    def cls_id():
        return 'b81f9ae0-026e-11d3-9c1f-00c04f5aa6ed'

    def read(self, stream: Stream, version):
        self.color = stream.read_object('color')
        self.symbol_level = SymbolLayer.read_symbol_level(stream)
        stream.read_int('unknown int')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'color': self.color.to_dict() if self.color is not None else None,
            'type': 'ColorSymbol'
        }


class GradientFillSymbol(FillSymbolLayer):
    """
    Gradient fill symbol layer
    """

    LINEAR = 0
    RECTANGULAR = 1
    CIRCULAR = 2
    BUFFERED = 3

    @staticmethod
    def cls_id():
        return '7914e609-c892-11d0-8bb6-080009ee4e41'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.ramp = None
        self.type = None
        self.percent = 0
        self.intervals = 5
        self.angle = 0
        self.fill_color = None

    @staticmethod
    def convert_gradient_type(gradient_type: int) -> str:
        """
        Converts a gradient type to string
        """
        if gradient_type == GradientFillSymbol.LINEAR:
            return 'linear'
        elif gradient_type == GradientFillSymbol.CIRCULAR:
            return 'circular'
        elif gradient_type == GradientFillSymbol.BUFFERED:
            return 'buffered'
        elif gradient_type == GradientFillSymbol.RECTANGULAR:
            return 'rectangular'
        raise NotImplementedException('Gradient type {} not implemented yet'.format(gradient_type))

    def to_dict(self) -> dict:  # pylint: disable=method-hidden
        out = {'ramp': self.ramp.to_dict(),
               'percent': self.percent,
               'angle': self.angle,
               'intervals': self.intervals,
               'fill_color': self.fill_color.to_dict() if self.fill_color else None,
               'gradient_type': self.convert_gradient_type(self.type)}
        if self.outline:
            out['outline'] = self.outline.to_dict()

        return out

    def children(self):
        res = super().children()
        if self.ramp:
            res.append(self.ramp)
        return res

    def read(self, stream: Stream, version):
        self.ramp = stream.read_object('Color ramp')
        self.fill_color = stream.read_object('fill color')

        # either an entire LineSymbol or just a LineSymbolLayer
        self.outline = stream.read_object('outline')

        self.percent = stream.read_double('percent')
        self.intervals = stream.read_uint('intervals')
        self.angle = stream.read_double('angle')

        self.type = stream.read_uint('Gradient type')
        self.symbol_level = SymbolLayer.read_symbol_level(stream)


class LineFillSymbol(FillSymbolLayer):
    """
    Line fill symbol layer
    """

    @staticmethod
    def cls_id():
        return '7914e606-c892-11d0-8bb6-080009ee4e41'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.angle = 0
        self.offset = 0
        self.separation = 0
        self.line = None

    def to_dict(self):  # pylint: disable=method-hidden
        out = {'line_symbol': self.line.to_dict() if self.line is not None else None, 'angle': self.angle,
               'offset': self.offset, 'separation': self.separation}
        if self.outline:
            out['outline'] = self.outline.to_dict()

        return out

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
        self.outline = stream.read_object('outline')

        self.angle = stream.read_double('angle')
        self.offset = stream.read_double('offset')
        self.separation = stream.read_double('separation')

        self.symbol_level = SymbolLayer.read_symbol_level(stream)


class MarkerFillSymbol(FillSymbolLayer):
    """
    Marker fill symbol layer
    """

    @staticmethod
    def cls_id():
        return '7914e608-c892-11d0-8bb6-080009ee4e41'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.random = False
        self.offset_x = 0
        self.offset_y = 0
        self.separation_x = 0
        self.separation_y = 0
        self.marker = None
        self.grid_angle = 0

    def to_dict(self):  # pylint: disable=method-hidden
        out = {'marker': None if self.marker is None else self.marker.to_dict(), 'offset_x': self.offset_x,
               'offset_y': self.offset_y, 'separation_x': self.separation_x, 'separation_y': self.separation_y,
               'random': self.random, 'grid_angle': self.grid_angle}
        if self.outline:
            out['outline'] = self.outline.to_dict()
        return out

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
        self.outline = stream.read_object('outline')

        self.symbol_level = SymbolLayer.read_symbol_level(stream)

        self.grid_angle = stream.read_double('grid angle')


class PictureFillSymbol(FillSymbolLayer):
    """
    Picture fill symbol layer
    """

    @staticmethod
    def cls_id():
        return 'd842b082-330c-11d2-9168-0000f87808ee'

    def __init__(self):  # pylint: disable=useless-super-delegation
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
        return [3, 4, 7, 8]

    def to_dict(self):  # pylint: disable=method-hidden
        out = {
            'color_foreground': self.color_foreground.to_dict() if self.color_foreground is not None else None,
            'color_foreground_model': self.color_foreground.model if self.color_foreground else None,
            'color_background': self.color_background.to_dict() if self.color_background is not None else None,
            'color_background_model': self.color_background.model,
            'color_transparent': self.color_transparent.to_dict() if self.color_transparent is not None else None,
            'color_transparent_model': None if not self.color_transparent else self.color_transparent.model,
            'swap_fg_bg': self.swap_fb_gb,
        }

        if self.outline:
            out['outline'] = self.outline.to_dict()

        out['picture'] = None if self.picture is None else self.picture.to_dict()
        out['angle'] = self.angle
        out['scale_x'] = self.scale_x
        out['scale_y'] = self.scale_y
        out['offset_x'] = self.offset_x
        out['offset_y'] = self.offset_y
        out['separation_x'] = self.separation_x
        out['separation_y'] = self.separation_y
        return out

    def read(self, stream: Stream, version):
        if version <= 4:
            self.picture = stream.read_object('picture')
        elif version == 7:
            _ = stream.read_ushort('pic version?')
            _ = stream.read_uint('picture type?')
            self.picture = stream.read_object('picture')
        elif version == 8:
            self.picture = Picture.create_from_stream(stream)

        self.color_background = stream.read_object('color bg')
        self.color_foreground = stream.read_object('color fg')
        self.color_transparent = stream.read_object('color trans')

        # either an entire LineSymbol or just a LineSymbolLayer
        self.outline = stream.read_object('outline')

        self.angle = stream.read_double('angle')
        self.scale_x = stream.read_double('scale_x')
        self.scale_y = stream.read_double('scale_y')

        self.offset_x = stream.read_double('offset x')
        self.offset_y = stream.read_double('offset y')
        self.separation_x = stream.read_double('separation x')
        self.separation_y = stream.read_double('separation y')

        stream.read(16)

        self.symbol_level = SymbolLayer.read_symbol_level(stream)

        self.swap_fb_gb = bool(stream.read_uchar('swap fgbg'))

        if version < 4:
            return

        stream.read(6)
        if 4 < version < 8:
            stream.read(4)
