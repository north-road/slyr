#!/usr/bin/env python
"""
Symbol layers base class
"""

import binascii
from slyr.parser.object import Object
from slyr.parser.stream import Stream
from slyr.parser.exceptions import UnreadableSymbolException


class SymbolLayer(Object):
    """
    Base class for symbol layers
    """

    def __init__(self):
        self.locked = False
        self.enabled = True

    def read_enabled(self, stream: Stream):
        """
        Reads the layer 'enabled' state
        """
        enabled = stream.read_uint()
        self.enabled = enabled == 1
        stream.log('read enabled ({})'.format(self.enabled), 4)

    def read_locked(self, stream: Stream):
        """
        Reads the layer 'locked' state

        """
        locked = stream.read_uint()
        self.locked = locked == 1
        stream.log('read layer locked ({})'.format(self.locked), 4)

    @staticmethod
    def read_0d_terminator(stream):
        """
        Tries the read the standard 0d00000000000000 layer terminator,
        raising a UnreadableSymbolException if it's not found.
        """
        check = binascii.hexlify(stream.read(8))
        if check != b'0d00000000000000':
            raise UnreadableSymbolException('Did not find expected layer terminator, got {} at {}'.format(check, hex(stream.tell() - 8)))
