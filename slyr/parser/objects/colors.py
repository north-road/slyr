#!/usr/bin/env python

import binascii
from struct import unpack
from slyr.parser.object import Object
from slyr.parser.color_parser import InvalidColorException, cielab_to_rgb
from slyr.parser.object_registry import REGISTRY

"""
Extracts colors from a style blob
"""


class Color(Object):

    def __init__(self):
        self.model = ''
        self.dither = False
        self.is_null = False

    def read_color(self, stream):
        pass

    def to_dict(self) -> dict:
        return {}

    def read(self, stream):
        start = stream.tell()
        self.read_color(stream)

        self.dither = binascii.hexlify(stream.read(1)) == b'01'
        self.is_null = binascii.hexlify(stream.read(1)) == b'ff'

        if stream.debug:
            print('Read color ({}) at {} {}'.format(self.model, hex(start), self.to_dict()))


class RgbColor(Color):

    def __init__(self):
        super().__init__()
        self.model = 'rgb'
        self.red = 0
        self.green = 0
        self.blue = 0

    @staticmethod
    def guid():
        return '7ee9c496-d123-11d0-8383-080009b996cc'

    def read_color(self, stream):
        if self.model == 'rgb':
            if stream.debug:
                print('Skipping some bytes at {}'.format(hex(stream.tell())))

            terminator = binascii.hexlify(stream.read(2))
            if not terminator == b'0100':
                # .lyr files have an extra 4 bytes in here - of unknown purpose
                stream.read(4)

            start = stream.tell()
            terminator = binascii.hexlify(stream.read(1))
            if terminator != b'01':
                if stream.debug:
                    print('Expected 01 at {}, got {}'.format(hex(start), terminator))

                raise InvalidColorException('Expected 01 at {}, got {}'.format(hex(start), terminator))

            # another two unknown bytes
            stream.read(2)
        elif self.model == 'hsv':
            if stream.debug:
                print('Skipping 5 bytes at {}'.format(hex(stream.tell())))

            stream.read(5)

        lab_l = stream.read_double()
        lab_a = stream.read_double()
        lab_b = stream.read_double()

        try:
            self.red, self.green, self.blue = cielab_to_rgb(lab_l, lab_a, lab_b)
        except OverflowError:
            raise InvalidColorException()

        if self.red > 255 or self.red < 0 or self.blue > 255 or self.blue < 0 or self.green > 255 or self.green < 0:
            raise InvalidColorException()

    def to_dict(self):
        return {'R': self.red, 'G': self.green, 'B': self.blue, 'dither': self.dither, 'is_null': self.is_null}


class CMYKColor(Color):

    def __init__(self):
        super().__init__()
        self.model = 'cmyk'

        self.cyan = 0
        self.magenta = 0
        self.yellow = 0
        self.black = 0

    @staticmethod
    def guid():
        return '7ee9c497-d123-11d0-8383-080009b996cc'

    def read_color(self, stream):
        if stream.debug:
            print('Skipping 4 bytes at {}'.format(hex(stream.tell())))
        stream.read(4)

        # CMYK is nice and easy - it's just direct char representations of the C/M/Y/K integer components!
        self.cyan = unpack("B", stream.read(1))[0]
        self.magenta = unpack("B", stream.read(1))[0]
        self.yellow = unpack("B", stream.read(1))[0]
        self.black = unpack("B", stream.read(1))[0]

    def to_dict(self):
        return {'C': self.cyan, 'M': self.magenta, 'Y': self.yellow, 'K': self.black}


class HSVColor(RgbColor):

    def __init__(self):
        super().__init__()
        self.model = 'hsv'

    @staticmethod
    def guid():
        return '7ee9c492-d123-11d0-8383-080009b996cc'


class HSLColor(RgbColor):

    @staticmethod
    def guid():
        return '7ee9c493-d123-11d0-8383-080009b996cc'


class GrayColor(RgbColor):

    @staticmethod
    def guid():
        return '7ee9c495-d123-11d0-8383-080009b996cc'


REGISTRY.register_object(CMYKColor)
REGISTRY.register_object(RgbColor)
REGISTRY.register_object(HSVColor)
REGISTRY.register_object(HSLColor)
REGISTRY.register_object(GrayColor)