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
        self.tags = ''

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

    def read_tags(self, stream: Stream):
        """
        Reads the layer tags

        """
        self.tags = stream.read_string('layer tags')
