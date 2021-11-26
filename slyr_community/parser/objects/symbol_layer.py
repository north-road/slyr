#!/usr/bin/env python
"""
Symbol layers base class

COMPLETE INTERPRETATION
"""

import functools
from slyr_community.parser.object import Object
from slyr_community.parser.stream import Stream
from slyr_community.parser.exceptions import NotImplementedException


class SymbolLayer(Object):
    """
    Base class for symbol layers
    """

    def __init__(self):
        super().__init__()
        self.locked = False
        self.enabled = True
        self.tags = ''
        self.symbol_level = 0

        def to_dict_(func):
            """
            Adds common attributes to the to_dict function
            """

            @functools.wraps(func)
            def wrapper(*args, **kwargs):  # pylint: disable=unused-argument
                """
                Wrapper which adds common attributes to the to_dict call
                """
                d = func()
                if d is not None:
                    d['enabled'] = self.enabled
                    d['locked'] = self.locked
                    d['symbol_level'] = self.symbol_level
                    if self.tags:
                        d['tags'] = self.tags
                return d

            return wrapper

        self.to_dict = to_dict_(self.to_dict)

    def to_dict(self):  # pylint: disable=method-hidden
        raise NotImplementedException('{} not implemented yet'.format(self.__class__))

    def read_enabled(self, stream: Stream):
        """
        Reads the layer 'enabled' state
        """
        self.enabled = stream.read_uint('enabled') != 0

    def read_locked(self, stream: Stream):
        """
        Reads the layer 'locked' state

        """
        self.locked = stream.read_uint('locked') != 0

    def read_tags(self, stream: Stream):
        """
        Reads the layer tags

        """
        self.tags = stream.read_string('layer tags')

    @staticmethod
    def read_symbol_level(stream: Stream):
        """
        Reads the symbol level from the stream
        """
        # actually raster op
        stream.read_int('raster op', expected=13)
        # symbol level of 0xffffffff = merge and join
        return stream.read_int('symbol level')
