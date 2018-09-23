#!/usr/bin/env python

"""
Scans a binary blob for interesting looking bits, which may give clues to reverse engineering
"""

import string
from struct import unpack
import binascii
from colorama import Fore

from slyr.parser.stream import Stream
from slyr.parser.object_registry import REGISTRY
from slyr.parser.objects.colors import Color


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
        res = self.check_handle(file_handle)  # pylint: disable=assignment-from-none
        file_handle.seek(start)
        return res

    def check_handle(self, file_handle):  # pylint: disable=unused-argument
        """
        Runs scan check. Subclasses should implement their logic here
        :param file_handle: handle to scan
        :return: match if found, or None
        """
        return None


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
    def strip_non_ascii(s):
        """
        Removes all non-ascii characters from a string
        """
        return ''.join(filter(lambda x: x in StringScan.PRINTABLE, s))

    def check_handle(self, file_handle):
        try:
            start = file_handle.tell()
            string_value = Stream(file_handle).read_string()
            if string_value and StringScan.strip_non_ascii(string_value) == string_value:
                return StringMatch(start, file_handle.tell() - start, string_value)
        except:  # nopep8, pylint: disable=bare-except
            pass
        return None


class GuidCodeMatch(ObjectMatch):
    """
    Object code match
    """

    def __init__(self, match_start, match_length, found_type):
        super().__init__(match_start, match_length)
        self.found_type = found_type

    @staticmethod
    def precedence():
        return 100

    @staticmethod
    def color():
        return Fore.CYAN

    def value(self):
        return self.found_type


class GuidCodeScan(ObjectScan):
    """
    Scans for GUIDs
    """

    def check_handle(self, file_handle):
        try:
            guid_bin = binascii.hexlify(file_handle.read(16))
            guid = REGISTRY.hex_to_guid(guid_bin)

            # check first in unimplemented types
            if guid in REGISTRY.NOT_IMPLEMENTED_GUIDS:
                return GuidCodeMatch(file_handle.tell() - 16, 16, REGISTRY.NOT_IMPLEMENTED_GUIDS[guid])

            obj = REGISTRY.create_object(guid)
            if obj is None:
                return None
            return GuidCodeMatch(file_handle.tell() - 16, 16, str(obj.__class__.__name__))
        except:  # nopep8, pylint: disable=bare-except
            pass
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
        except:  # nopep8, pylint: disable=bare-except
            pass
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
        except:  # nopep8, pylint: disable=bare-except
            pass
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
        if self.color_model in ('rgb', 'hsv'):
            return str(self.matched_color['R']) + ',' + str(self.matched_color['G']) + ',' + str(
                self.matched_color['B'])
        elif self.color_model == 'cmyk':
            return 'CMYK:' + str(self.matched_color['C']) + ',' + str(self.matched_color['M']) + ',' + str(
                self.matched_color['Y']) + ',' + str(self.matched_color['K'])
        return None


class ColorScan(ObjectScan):
    """
    Scans for color values
    """

    def check_handle(self, file_handle):
        try:
            start = file_handle.tell()
            stream = Stream(file_handle)
            color = stream.read_object()
            if issubclass(color.__class__, Color):
                return ColorMatch(start, file_handle.tell() - start, color.color_model, color)
            else:
                return None
        except:  # nopep8, pylint: disable=bare-except
            pass
        return None


SCANNERS = [StringScan(), GuidCodeScan(), DoubleScan(), IntScan(),
            ColorScan()]
