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
        return [4]

    def read(self, stream: Stream, version):
        self.color = stream.read_object('color')

        self.unicode = stream.read_int('unicode')
        self.angle = stream.read_double('angle')
        self.size = stream.read_double('size')
        self.x_offset = stream.read_double('x offset')
        self.y_offset = stream.read_double('y offset')

        # unknown - ends with FFFF
        while not binascii.hexlify(stream.read(2)) == b'ffff':
            stream.rewind(1)

        self.font = stream.read_string('font name')

        # large unknown block
        protector = 0
        while not binascii.hexlify(stream.read(2)) == b'9001':
            stream.rewind(1)
            protector += 1
            if protector > 100:
                raise UnreadableSymbolException('Could not find end point of character marker')
        stream.read(4)
        stream.read(6)

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
        self.read_0d_terminator(stream)

        self.x_offset = stream.read_double('x offset')
        self.y_offset = stream.read_double('y offset')

        check = binascii.hexlify(stream.read(2))
        if check != b'ffff':
            raise UnreadableSymbolException('Expected ffff at {}, got {}'.format(check, hex(stream.tell() - 2)))
