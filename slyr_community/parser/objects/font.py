#!/usr/bin/env python
"""
std OLE Font

COMPLETE INTERPRETATION
"""

import binascii
from slyr_community.parser.object import Object
from slyr_community.parser.stream import Stream
from slyr_community.parser.exceptions import UnsupportedVersionException


class Font(Object):
    """
    A standard OLE font object
    """

    NoAttributes = 0
    Italic = 2
    Underline = 4
    Strikethrough = 8

    # see lfCharSet values
    CHARSET_MAP = {
        0: 'cp1252',  # ANSI
        1: 'cp1252',  # DEFAULT_CHARSET
        2: 'cp1251',  # SYMBOL_CHARSET
        128: 'cp932',  # SHIFTJIS_CHARSET
        129: 'cp949',  # HANGUL_CHARSET
        130: 'cp1361',  # JOHAB
        134: 'cp936',  # GB2312_CHARSET
        136: 'cp950',  # CHINESEBIG5_CHARSET
        161: 'cp1253',  # GREEK_CHARSET
        162: 'cp1254',  # TURKISH_CHARSET
        163: 'cp1258',  # VIETNAMESE
        177: 'cp1255',  # HEBREW
        178: 'cp1256',  # ARABIC
        186: 'cp1257',  # BALTIC_CHARSET
        204: 'cp1251',  # RUSSIAN_CHARSET
        222: 'cp874',  # THAI
        238: 'cp1250',  # EASTEUROPE_CHARSET
        # MAC_CHARSET? (77?)
        # OEM_CHARSET (255)
    }

    @staticmethod
    def cls_id():
        return '0be35203-8f91-11ce-9de3-00aa004bb851'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.charset = None
        self.weight = None
        self.size = None
        self.font_name = ''
        self.italic = False
        self.underline = False
        self.strikethrough = False

    @staticmethod
    def compatible_versions():
        return None

    def to_dict(self):
        return {'font_name': self.font_name,
                'charset': self.charset,
                'weight': self.weight,
                'size': self.size,
                'italic': self.italic,
                'strikethrough': self.strikethrough,
                'underline': self.underline}

    def read(self, stream: Stream, version):
        version = binascii.hexlify(stream.read(1))
        if version != b'01':
            raise UnsupportedVersionException('Unsupported Font version {}'.format(version))

        self.charset = stream.read_ushort('charset')

        # Not exposed in ArcMap front end:
        attributes = stream.read_uchar('attributes')
        self.italic = bool(attributes & self.Italic)
        self.underline = bool(attributes & self.Underline)
        self.strikethrough = bool(attributes & self.Strikethrough)

        self.weight = stream.read_ushort('weight')

        # From https://docs.microsoft.com/en-us/windows/desktop/api/olectl/ns-olectl-tagfontdesc
        # Use the int64 member of the CY structure and scale your font size (in points) by 10000.
        self.size = stream.read_int('font size') / 10000

        name_length = stream.read_uchar('font name size')
        self.font_name = stream.read(name_length).decode(Font.CHARSET_MAP[self.charset])
