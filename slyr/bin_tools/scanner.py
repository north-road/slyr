#!/usr/bin/env python

"""
Scans a binary blob for interesting looking bits, which may give clues to reverse engineering
"""

import string
from struct import unpack
import binascii
from colorama import Fore

from slyr.parser.symbol_parser import read_string, Handle, read_color, read_magic_2
from slyr.parser.color_parser import read_color_model, read_color_and_model, InvalidColorException


class ObjectScan:
    """
    Base class for objects which scan through file handles for interesting bits
    """

    def scan(self, file_handle):
        """
        Scan the given file handle for a potential match
        :param file_handle: handle to scan
        :return: match if found, or None
        """
        start = file_handle.tell()
        res = self.check_handle(file_handle)
        file_handle.seek(start)
        return res

    def check_handle(self, file_handle):
        """
        Runs scan check. Subclasses should implement their logic here
        :param file_handle: handle to scan
        :return: match if found, or None
        """
        pass


class ObjectMatch:
    """
    Result from finding a scan match
    """

    def __init__(self, match_start, match_length):
        """
        Constructor for ObjectMatch
        :param match_start: start of match
        :param match_length: length of match
        """
        self.match_start = match_start
        self.match_length = match_length
        self.match_end = match_start + match_length

    @staticmethod
    def precedence():
        """
        Precedence, determines which coloring an individual byte should get. Higher is better.
        """
        return 1

    @staticmethod
    def color():
        """
        Returns the color for shading this match
        """
        return Fore.WHITE

    def value(self):
        """
        Returns a string representation of the match
        """
        return ''


class StringMatch(ObjectMatch):
    """
    Encoded string match
    """

    def __init__(self, match_start, match_length, found_string):
        super().__init__(match_start, match_length)
        self.found_string = found_string

    @staticmethod
    def precedence():
        return 100

    @staticmethod
    def color():
        return Fore.RED

    def value(self):
        return '"' + self.found_string + '"'


class StringScan(ObjectScan):
    """
    Scans for encoded strings
    """
    PRINTABLE = set(string.printable)

    @staticmethod
    def strip_non_ascii(string):
        return ''.join(filter(lambda x: x in StringScan.PRINTABLE, string))

    def check_handle(self, file_handle):
        try:
            start = file_handle.tell()
            string_value = read_string(Handle(file_handle))
            if string_value and StringScan.strip_non_ascii(string_value) == string_value:
                return StringMatch(start, file_handle.tell() - start, string_value)
        except:  # nopep8
            return None


class ObjectCodeMatch(ObjectMatch):
    """
    Object code match
    """

    def __init__(self, match_start, match_length, found_type):
        super().__init__(match_start, match_length)
        self.found_type = found_type

    @staticmethod
    def precedence():
        return 50

    @staticmethod
    def color():
        return Fore.CYAN

    def value(self):
        return self.found_type


class ObjectCodeScan(ObjectScan):
    """
    Scans for encoded object types
    """
    OBJECT_DICT = {
        b'04e6': 'FillSymbol',
        b'ffe5': 'MarkerSymbol',
        b'fae5': 'LineSymbol',
        b'f9e5': 'SimpleLineSymbolLayer',
        b'fbe5': 'CartographicLineSymbolLayer',
        b'03e6': 'SimpleFillSymbolLayer',
        b'fee5': 'SimpleMarkerSymbolLayer',
        b'00e6': 'CharacterMarkerSymbolLayer',
        b'02e6': 'PictureMarkerSymbolLayer',
        b'09e6': 'GradientFillSymbolLayer',
        b'3194': 'ArrowMarkerSymbolLayer'
    }

    def check_handle(self, file_handle):
        try:
            object_type = binascii.hexlify(file_handle.read(2))
            if object_type in self.OBJECT_DICT:
                return ObjectCodeMatch(file_handle.tell() - 2, 2, self.OBJECT_DICT[object_type])
        except:  # nopep8
            return None


class DoubleMatch(ObjectMatch):
    """
    Real/double value match
    """

    def __init__(self, match_start, match_length, found_value):
        super().__init__(match_start, match_length)
        self.found_value = found_value

    @staticmethod
    def precedence():
        return 30

    @staticmethod
    def color():
        return Fore.GREEN

    def value(self):
        return str(self.found_value)


class DoubleScan(ObjectScan):
    """
    Scans for reasonable real/double values
    """

    def check_handle(self, file_handle):
        try:
            real_value = unpack("<d", file_handle.read(8))[0]
            if -1000 < real_value < 10000 and (real_value > 0.00001 or real_value < -0.00001) \
                    and round(real_value * 10) == real_value * 10:
                return DoubleMatch(file_handle.tell() - 8, 8, real_value)
        except:  # nopep8
            return None


class IntMatch(ObjectMatch):
    """
    Integer value match
    """

    def __init__(self, match_start, match_length, found_value):
        super().__init__(match_start, match_length)
        self.found_value = found_value

    @staticmethod
    def precedence():
        return 20

    @staticmethod
    def color():
        return Fore.YELLOW

    def value(self):
        return str(self.found_value)


class IntScan(ObjectScan):
    """
    Scans for reasonable integer values
    """

    def check_handle(self, file_handle):
        try:
            int_value = unpack("<I", file_handle.read(4))[0]
            if -100 < int_value < 255 and int_value != 0:
                return IntMatch(file_handle.tell() - 4, 4, int_value)
        except:  # nopep8
            return None


class Magic1Match(ObjectMatch):
    """
    Match for magic number 1
    """

    def __init__(self, match_start, match_length, match_string):
        super().__init__(match_start, match_length)
        self.match_string = match_string

    @staticmethod
    def precedence():
        return 25

    @staticmethod
    def color():
        return Fore.BLUE

    def value(self):
        return self.match_string


class Magic1Scan(ObjectScan):
    """
    Scans for magic number 1
    """

    def check_handle(self, file_handle):
        try:
            magic = binascii.hexlify(file_handle.read(14))
            if magic == b'147992c8d0118bb6080009ee4e41' or magic == b'53886ee0d111b2770000f878229e':
                return Magic1Match(file_handle.tell() - 14, 14, magic.decode('UTF-8'))
        except:  # nopep8
            return None


class Magic2Match(ObjectMatch):
    """
    Magic number 2 match
    """

    def __init__(self, match_start, match_length):
        super().__init__(match_start, match_length)

    @staticmethod
    def precedence():
        return 25

    @staticmethod
    def color():
        return Fore.LIGHTBLUE_EX

    def value(self):
        return 'c4e97e23d1d0118383080009b996cc'


class Magic2Scan(ObjectScan):
    """
    Scans for magic number 2
    """

    def check_handle(self, file_handle):
        try:
            magic = binascii.hexlify(file_handle.read(15))
            if magic == b'c4e97e23d1d0118383080009b996cc':
                return Magic2Match(file_handle.tell() - 15, 15)
        except:  # nopep8
            return None


class ColorMatch(ObjectMatch):
    """
    Color match
    """

    def __init__(self, match_start, match_length, color_model, matched_color):
        super().__init__(match_start, match_length)
        self.matched_color = matched_color
        self.color_model = color_model

    @staticmethod
    def precedence():
        return 80

    @staticmethod
    def color():
        return Fore.MAGENTA

    def value(self):
        if self.color_model == 'rgb':
            return str(self.matched_color['R']) + ',' + str(self.matched_color['G']) + ',' + str(self.matched_color['B'])
        elif self.color_model == 'cmyk':
            return 'CMYK:' + str(self.matched_color['C']) + ',' + str(self.matched_color['M']) + ',' + str(self.matched_color['Y']) + ',' + str(self.matched_color['K'])
        else:
            assert False


class ColorScan(ObjectScan):
    """
    Scans for color values
    """

    def check_handle(self, file_handle):
        try:
            start = file_handle.tell()
            color_model, color = read_color_and_model(file_handle, True)
            print(color_model, color)
          #  if True or (color['R'] == 255 or color['G'] == 255 or color['B'] == 255) and (
          #          not color['dither'] and not color['is_null']):
            return ColorMatch(start, file_handle.tell() - start, color_model, color)
        except InvalidColorException:  # nopep8
            return None


SCANNERS = [StringScan(), ObjectCodeScan(), DoubleScan(), IntScan(), Magic1Scan(), Magic2Scan(), ColorScan()]
