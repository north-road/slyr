#!/usr/bin/env python
"""
Color objects
"""

import binascii
from slyr.parser.object import Object
from slyr.parser.exceptions import InvalidColorException
from slyr.parser.color_parser import cielab_to_rgb


class Color(Object):
    """
    Base class for color objects
    """

    def __init__(self):
        self.model = ''
        self.dither = False
        self.is_null = False

    def read_color(self, stream):  # pylint: disable=unused-argument
        """
        Reads the color from the stream. Subclasses must implement this
        """
        assert False

    def to_dict(self) -> dict:
        """
        Returns a dictionary representation of the color
        :return:
        """
        return {}

    def read(self, stream):
        self.read_color(stream)

        self.dither = binascii.hexlify(stream.read(1)) == b'01'
        self.is_null = binascii.hexlify(stream.read(1)) == b'ff'

        stream.log('Read color ({}) of {}'.format(self.model, self.to_dict()))


class RgbColor(Color):
    """
    RGB Color
    """

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

        if self.red > 255 or self.red < 0:
            raise InvalidColorException()
        if self.blue > 255 or self.blue < 0:
            raise InvalidColorException()
        if self.green > 255 or self.green < 0:
            raise InvalidColorException()

    def to_dict(self):
        return {'R': self.red, 'G': self.green, 'B': self.blue, 'dither': self.dither, 'is_null': self.is_null}


class CMYKColor(Color):
    """
    CYMK Color
    """

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
    """
    HSV Color
    """

    def __init__(self):
        super().__init__()
        self.model = 'hsv'

    @staticmethod
    def guid():
        return '7ee9c492-d123-11d0-8383-080009b996cc'


class HSLColor(RgbColor):
    """
    HSL Color, actually exposed in ArcGIS as a "named color" (I think)
    """

    @staticmethod
    def guid():
        return '7ee9c493-d123-11d0-8383-080009b996cc'


class GrayColor(RgbColor):
    """
    Grayscale Color
    """

    @staticmethod
    def guid():
        return '7ee9c495-d123-11d0-8383-080009b996cc'
