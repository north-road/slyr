#!/usr/bin/env python

import binascii
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

        stream.log('Read color ({}) of {}'.format(self.model, self.to_dict()))


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
        stream.log('Skipping 5 bytes')  # looks like 01 00 01 00 00 ?
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
        stream.log('Skipping 4 bytes')
        stream.read(4)

        # CMYK is nice and easy - it's just direct char representations of the C/M/Y/K integer components!
        self.cyan = stream.read_uchar()
        self.magenta = stream.read_uchar()
        self.yellow = stream.read_uchar()
        self.black = stream.read_uchar()

    def to_dict(self):
        return {'C': self.cyan, 'M': self.magenta, 'Y': self.yellow, 'K': self.black, 'dither': self.dither,
                'is_null': self.is_null}


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


REGISTRY.register(CMYKColor)
REGISTRY.register(RgbColor)
REGISTRY.register(HSVColor)
REGISTRY.register(HSLColor)
REGISTRY.register(GrayColor)
