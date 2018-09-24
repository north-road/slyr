#!/usr/bin/env python
"""
std OLE Font
"""

import binascii
from slyr.parser.object import Object
from slyr.parser.stream import Stream
from slyr.parser.exceptions import UnsupportedVersionException


class Font(Object):
    """
    A standard OLE font object
    """

    NoAttributes = 0
    Italic = 2
    Underline = 4
    Strikethrough = 8

    def __init__(self):
        super().__init__()
        self.charset = None
        self.weight = None
        self.size = None
        self.font_name = ''
        self.italic = False
        self.underline = False
        self.strikethrough = False

    @staticmethod
    def guid():
        return '0be35203-8f91-11ce-9de3-00aa004bb851'

    @staticmethod
    def compatible_versions():
        return None

    def read(self, stream: Stream, version):
        version = binascii.hexlify(stream.read(1))
        if version != b'01':
            raise UnsupportedVersionException('Unsupported Font version {}'.format(version))

        self.charset = stream.read_ushort('charset')

        # Not exposed in ArcMap front end:
        attributes = stream.read_uchar('attributes')
        self.italic = attributes & self.Italic
        self.underline = attributes & self.Underline
        self.strikethrough = attributes & self.Strikethrough

        self.weight = stream.read_ushort('weight')

        # From https://docs.microsoft.com/en-us/windows/desktop/api/olectl/ns-olectl-tagfontdesc
        # Use the int64 member of the CY structure and scale your font size (in points) by 10000.
        self.size = stream.read_int('font size') / 10000

        name_length = stream.read_uchar('font name size')
        self.font_name = stream.read(name_length).decode()
