#!/usr/bin/env python
"""
Marker symbol layers

COMPLETE INTERPRETATION of most common subclasses
"""

import binascii
from slyr_community.parser.objects.symbol_layer import SymbolLayer
from slyr_community.parser.stream import Stream
from slyr_community.parser.exceptions import UnreadableSymbolException


class MarkerSymbolLayer(SymbolLayer):
    """
    Base class for marker symbol layers
    """

    @staticmethod
    def compatible_versions():
        return [2]


class SimpleMarkerSymbol(MarkerSymbolLayer):
    """
    Simple marker symbol layer
    """

    @staticmethod
    def cls_id():
        return '7914e5fe-c892-11d0-8bb6-080009ee4e41'

    @staticmethod
    def compatible_versions():
        return [1, 2]

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.type = None
        self.color = None
        self.size = 0
        self.x_offset = 0
        self.y_offset = 0
        self.outline_enabled = False
        self.outline_color = None
        self.outline_width = 0.0
        self.rotate_with_transform = False
        self.angle = 0

    def to_dict(self):
        out = {
            'color': self.color.to_dict() if self.color is not None else None,
            'marker_type': self.type,
            'size': self.size,
            'x_offset': self.x_offset,
            'y_offset': self.y_offset,
            'outline_enabled': self.outline_enabled,
            'outline_color': self.outline_color.to_dict(),
            'outline_size': self.outline_width,
            'rotate_with_transform': self.rotate_with_transform,
            'angle': self.angle
        }
        return out

    def children(self):
        res = super().children()
        if self.color:
            res.append(self.color)
        return res

    def read(self, stream: Stream, version):
        self.color = stream.read_object('color')
        self.size = stream.read_double('size')

        type_code = stream.read_int()
        type_dict = {
            0: 'circle',
            1: 'square',
            2: 'cross',
            3: 'x',
            4: 'diamond'
        }

        if type_code not in type_dict:
            raise UnreadableSymbolException(
                'Unknown marker type at {}, got {}'.format(hex(stream.tell() - 4),
                                                           type_code))
        stream.log('found a {}'.format(type_dict[type_code]), 4)
        self.type = type_dict[type_code]

        self.symbol_level = SymbolLayer.read_symbol_level(stream)
        self.angle = stream.read_double('angle')
        self.x_offset = stream.read_double('x offset')
        self.y_offset = stream.read_double('y offset')

        self.outline_enabled = stream.read_uchar('has outline') != 0
        self.outline_width = stream.read_double('outline width')
        self.outline_color = stream.read_object('outline color')

        if version > 1:
            self.rotate_with_transform = stream.read_ushort('rotate with transform') != 0


class CharacterMarkerSymbol(MarkerSymbolLayer):
    """
    Character marker symbol layer
    """

    @staticmethod
    def cls_id():
        return '7914e600-c892-11d0-8bb6-080009ee4e41'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.type = None
        self.color = None
        self.size = 0
        self.unicode = 0
        self.x_offset = 0
        self.y_offset = 0
        self.angle = 0
        self.outline_enabled = False
        self.outline_color = None
        self.outline_width = 0.0
        self.font = None
        self.std_font = None
        self.x_scale = 1
        self.y_scale = 1
        self.rotate_with_transform = False

    @staticmethod
    def compatible_versions():
        return [1, 2, 3, 4]

    def to_dict(self):
        out = {
            'color': self.color.to_dict() if self.color is not None else None,
            'unicode': self.unicode,
            'font': self.font,
            'std_font': self.std_font.to_dict() if self.std_font is not None else None,
            'size': self.size,
            'angle': self.angle,
            'x_offset': self.x_offset,
            'y_offset': self.y_offset,
            'x_scale': self.x_scale,
            'y_scale': self.y_scale,
            'rotate_with_transform': self.rotate_with_transform
        }
        return out

    def children(self):
        res = super().children()
        if self.color:
            res.append(self.color)
        if self.outline_color:
            res.append(self.outline_color)
        if self.std_font:
            res.append(self.std_font)
        return res

    def read(self, stream: Stream, version):
        self.color = stream.read_object('color')

        self.unicode = stream.read_int('unicode')
        self.angle = stream.read_double('angle')
        self.size = stream.read_double('size')
        self.x_offset = stream.read_double('x offset')
        self.y_offset = stream.read_double('y offset')

        self.x_scale = stream.read_double('x scale')
        self.y_scale = stream.read_double('y scale')

        if version <= 2:
            self.std_font = stream.read_object('font')
            self.font = self.std_font.font_name

        self.symbol_level = SymbolLayer.read_symbol_level(stream)
        if version > 1:
            self.rotate_with_transform = stream.read_ushort('rotate with transform') != 0

        if version >= 3:
            self.font = stream.read_string('font name')

            # lot of unknown stuff
            stream.read_double('unknown 3', expected=0)  # or object?
            stream.read_double('unknown 4', expected=0)  # or object?

            stream.read_int('font weight')
            stream.read_int('unknown', expected=0)
            stream.read_int('font size * 10000') / 10000

            if version >= 4:
                # std OLE font .. maybe contains useful stuff like bold/etc, but these aren't exposed in ArcGIS anyway..
                self.std_font = stream.read_object('font')


class ArrowMarkerSymbol(MarkerSymbolLayer):
    """
    Arrow marker symbol layer
    """

    @staticmethod
    def cls_id():
        return '88539431-e06e-11d1-b277-0000f878229e'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.type = None
        self.color = None
        self.size = 0
        self.width = 0
        self.x_offset = 0
        self.y_offset = 0
        self.angle = 0
        self.rotate_with_transform = False
        self.style = 0

    @staticmethod
    def compatible_versions():
        return [2]

    def children(self):
        res = super().children()
        if self.color:
            res.append(self.color)
        return res

    def to_dict(self):
        out = {
            'color': self.color.to_dict() if self.color is not None else None,
            'size': self.size,
            'width': self.width,
            'angle': self.angle,
            'x_offset': self.x_offset,
            'y_offset': self.y_offset,
            'rotate_with_transform': self.rotate_with_transform,
            'style': self.style
        }
        return out

    def read(self, stream: Stream, version):
        self.color = stream.read_object('color')

        self.size = stream.read_double('size')
        self.width = stream.read_double('width')
        self.angle = stream.read_double('angle')
        self.style = stream.read_uint('style')
        self.symbol_level = SymbolLayer.read_symbol_level(stream)

        self.x_offset = stream.read_double('x offset')
        self.y_offset = stream.read_double('y offset')

        self.rotate_with_transform = stream.read_ushort('rotate with transform') != 0


class PictureMarkerSymbol(MarkerSymbolLayer):
    """
    Picture marker symbol layer
    """

    @staticmethod
    def cls_id():
        return '7914e602-c892-11d0-8bb6-080009ee4e41'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.size = 0
        self.x_offset = 0
        self.y_offset = 0
        self.angle = 0

        self.picture = None

        self.color_foreground = None
        self.color_background = None
        self.color_transparent = None
        self.swap_fb_gb = False

        self.x_scale = 1
        self.y_scale = 1

        self.rotate_with_transform = False

    @staticmethod
    def compatible_versions():
        return [3, 4, 5, 7, 8, 9]

    def to_dict(self):
        out = {'color_foreground': self.color_foreground.to_dict() if self.color_foreground is not None else None,
               'color_background': self.color_background.to_dict() if self.color_background is not None else None,
               'color_transparent': self.color_transparent.to_dict() if self.color_transparent is not None else None,
               'size': self.size, 'angle': self.angle, 'x_offset': self.x_offset, 'y_offset': self.y_offset,
               'swap_fg_bg': self.swap_fb_gb,
               'x_scale': self.x_scale,
               'y_scale': self.y_scale,
               'rotate_with_transform': self.rotate_with_transform,
               'picture': None if self.picture is None else self.picture.to_dict()}

        return out

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

    def read(self, stream: Stream, version):
        if version in (3, 4, 5):
            self.picture = stream.read_object('picture')
        elif version in (7, 8):
            _ = stream.read_ushort('pic version?')
            _ = stream.read_uint('picture type?')
            self.picture = stream.read_object('picture')
        elif version == 9:
            self.picture = stream.read_picture('picture')

        if version < 4:
            _ = stream.read_object()
        if version <= 8:
            _ = stream.read_object()

        self.color_foreground = stream.read_object('color 1')
        self.color_background = stream.read_object('color 2')

        if version >= 9:
            self.color_transparent = stream.read_object('color 3')

        self.angle = stream.read_double('angle')
        self.size = stream.read_double('size')
        self.x_offset = stream.read_double('x offset')
        self.y_offset = stream.read_double('y offset')

        self.x_scale = stream.read_double('x scale')
        self.y_scale = stream.read_double('y scale')

        self.symbol_level = SymbolLayer.read_symbol_level(stream)
        self.swap_fb_gb = bool(stream.read_uchar('swap fgbg'))

        self.rotate_with_transform = stream.read_ushort('rotate with transform') != 0

        if version < 5:
            return

        stream.read_int('unknown', expected=0)
        stream.read_ushort('unknown', expected=0)
        if version == 7:
            return

        if 5 < version <= 8:
            size = stream.read_int('unknown size')
            stream.read(size)
