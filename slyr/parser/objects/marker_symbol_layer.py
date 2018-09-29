#!/usr/bin/env python
"""
Marker symbol layers
"""

import binascii
from slyr.parser.objects.symbol_layer import SymbolLayer
from slyr.parser.stream import Stream
from slyr.parser.exceptions import UnreadableSymbolException


class MarkerSymbolLayer(SymbolLayer):
    """
    Base class for marker symbol layers
    """

    def __init__(self):
        super().__init__()
        self.color = None
        self.outline_layer = None
        self.outline_symbol = None

    @staticmethod
    def compatible_versions():
        return [2]


class SimpleMarkerSymbolLayer(MarkerSymbolLayer):
    """
    Simple marker symbol layer
    """

    def __init__(self):
        super().__init__()
        self.type = None
        self.size = 0
        self.x_offset = 0
        self.y_offset = 0
        self.outline_enabled = False
        self.outline_color = None
        self.outline_width = 0.0

    @staticmethod
    def guid():
        return '7914e5fe-c892-11d0-8bb6-080009ee4e41'

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

        # look for 0d terminator
        if not binascii.hexlify(stream.read(8)) == b'0d00000000000000':
            raise UnreadableSymbolException()

        stream.read_double('unknown')

        self.x_offset = stream.read_double('x offset')
        self.y_offset = stream.read_double('y offset')

        has_outline = stream.read_uchar()
        if has_outline == 1:
            self.outline_enabled = True
        self.outline_width = stream.read_double('outline width')
        self.outline_color = stream.read_object('outline color')

        check = binascii.hexlify(stream.read(2))
        if check != b'ffff':
            raise UnreadableSymbolException('Expected ffff at {}, got {}'.format(check, hex(stream.tell() - 2)))


class CharacterMarkerSymbolLayer(MarkerSymbolLayer):
    """
    Character marker symbol layer
    """

    def __init__(self):
        super().__init__()
        self.type = None
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

    @staticmethod
    def guid():
        return '7914e600-c892-11d0-8bb6-080009ee4e41'

    @staticmethod
    def compatible_versions():
        return [2, 3, 4]

    def read(self, stream: Stream, version):
        self.color = stream.read_object('color')

        self.unicode = stream.read_int('unicode')
        self.angle = stream.read_double('angle')
        self.size = stream.read_double('size')
        self.x_offset = stream.read_double('x offset')
        self.y_offset = stream.read_double('y offset')

        stream.read_double('unknown 1')
        stream.read_double('unknown 2')

        if version == 2:
            self.std_font = stream.read_object('font')
            self.font = self.std_font.font_name

        stream.read_0d_terminator()
        if binascii.hexlify(stream.read(2)) != b'ffff':
            raise UnreadableSymbolException('Expected ffff')

        if version >= 3:
            self.font = stream.read_string('font name')

            # lot of unknown stuff
            stream.read_double('unknown 3')  # or object?
            stream.read_double('unknown 4')  # or object?

            stream.read_uchar('unknown')
            stream.read_uchar('unknown')

            stream.read(4)
            stream.read(6)

            if version >= 4:
                # std OLE font .. maybe contains useful stuff like bold/etc, but these aren't exposed in ArcGIS anyway..
                self.std_font = stream.read_object('font')


class ArrowMarkerSymbolLayer(MarkerSymbolLayer):
    """
    Arrow marker symbol layer
    """

    def __init__(self):
        super().__init__()
        self.type = None
        self.size = 0
        self.width = 0
        self.x_offset = 0
        self.y_offset = 0
        self.angle = 0

    @staticmethod
    def guid():
        return '88539431-e06e-11d1-b277-0000f878229e'

    @staticmethod
    def compatible_versions():
        return [2]

    def read(self, stream: Stream, version):
        self.color = stream.read_object('color')

        self.size = stream.read_double('size')
        self.width = stream.read_double('width')
        self.angle = stream.read_double('angle')

        # 12 bytes unknown purpose
        stream.log('skipping 12 unknown bytes')

        _ = stream.read_uint('unknown')
        stream.read_0d_terminator()

        self.x_offset = stream.read_double('x offset')
        self.y_offset = stream.read_double('y offset')

        check = binascii.hexlify(stream.read(2))
        if check != b'ffff':
            raise UnreadableSymbolException('Expected ffff at {}, got {}'.format(check, hex(stream.tell() - 2)))


class PictureMarkerSymbolLayer(MarkerSymbolLayer):
    """
    Picture marker symbol layer
    """

    def __init__(self):
        super().__init__()
        self.size = 0
        self.x_offset = 0
        self.y_offset = 0
        self.angle = 0

        self.file = None

        self.color_foreground = None
        self.color_background = None
        self.color_transparent = None
        self.swap_fb_gb = False

    @staticmethod
    def guid():
        return '7914e602-c892-11d0-8bb6-080009ee4e41'

    @staticmethod
    def compatible_versions():
        return [9]

    def read(self, stream: Stream, version):
        stream.read_int('unknown')
        stream.read_int('unknown 2')

        self.file = stream.read_embedded_file('image')

        self.color_foreground = stream.read_object('color 1')
        self.color_background = stream.read_object('color 2')
        self.color_transparent = stream.read_object('color 3')

        self.angle = stream.read_double('angle')
        self.size = stream.read_double('size')
        self.x_offset = stream.read_double('x offset')
        self.y_offset = stream.read_double('y offset')

        stream.read_double('unknown')
        stream.read_double('unknown')

        stream.read_0d_terminator()
        self.swap_fb_gb = bool(stream.read_uchar('swap fgbg'))

        check = binascii.hexlify(stream.read(2))
        if check != b'ffff':
            raise UnreadableSymbolException('Expected ffff at {}, got {}'.format(check, hex(stream.tell() - 2)))

        # unknown
        stream.read(6)
