#!/usr/bin/env python
"""
std OLE Font
"""

from struct import unpack
from slyr.parser.object import Object
from slyr.parser.stream import Stream


class Font(Object):
    """
    A standard OLE font object
    """

    def __init__(self):
        super().__init__()
        self.font = ''

    @staticmethod
    def guid():
        return '0be35203-8f91-11ce-9de3-00aa004bb851'

    def read(self, stream: Stream, version):
        stream.read(7)
        skip = unpack(">H", stream.read(2))[0]
        stream.log('font name for {}'.format(skip))
        stream.read(skip)
