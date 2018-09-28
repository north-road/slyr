#!/usr/bin/env python
"""
Extracts a symbol from a style blob
"""

from slyr.parser.stream import Stream
from slyr.parser.object import Object

from slyr.parser.exceptions import (UnreadableSymbolException,
                                    InvalidColorException)


class Symbol(Object):
    """
    Base class for symbols
    """

    def __init__(self):
        super().__init__()
        self.levels = []


class LineSymbol(Symbol):
    """
    Line symbol
    """

    @staticmethod
    def guid():
        return '7914e5fa-c892-11d0-8bb6-080009ee4e41'

    @staticmethod
    def compatible_versions():
        return [1, 2]

    def read(self, stream: Stream, version):
        if not stream.read_0d_terminator():
            raise UnreadableSymbolException('Could not find 0d terminator at {}'.format(hex(stream.tell() - 8)))

        number_layers = stream.read_uint('layer count')
        for i in range(number_layers):
            layer = stream.read_object('symbol layer {}/{}'.format(i + 1, number_layers))
            self.levels.extend([layer])

        for l in self.levels:
            l.read_enabled(stream)
        for l in self.levels:
            l.read_locked(stream)

        if version >= 2:
            for l in self.levels:
                l.read_tags(stream)


class FillSymbol(Symbol):
    """
    Fill symbol
    """

    @staticmethod
    def guid():
        return '7914e604-c892-11d0-8bb6-080009ee4e41'

    @staticmethod
    def compatible_versions():
        return [1, 2]

    def read(self, stream: Stream, version):
        if not stream.read_0d_terminator():
            raise UnreadableSymbolException('Could not find 0d terminator at {}'.format(hex(stream.tell() - 8)))

        _ = stream.read_object('unused color')

        number_layers = stream.read_int('layers')
        for i in range(number_layers):
            layer = stream.read_object('symbol layer {}/{}'.format(i + 1, number_layers))
            self.levels.extend([layer])

        # stream.read(4)
        for l in self.levels:
            l.read_enabled(stream)
        for l in self.levels:
            l.read_locked(stream)

        if version >= 2:
            for l in self.levels:
                l.read_tags(stream)


class MarkerSymbol(Symbol):
    """
    Marker symbol.

    """

    def __init__(self):
        super().__init__()
        self.halo = False
        self.halo_size = 0
        self.halo_symbol = None

    @staticmethod
    def guid():
        return '7914e5ff-c892-11d0-8bb6-080009ee4e41'

    @staticmethod
    def compatible_versions():
        return [2, 3]

    def read(self, stream: Stream, version):
        if not stream.read_0d_terminator():
            raise UnreadableSymbolException('Could not find 0d terminator at {}'.format(hex(stream.tell() - 8)))

        # consume unused properties - MultiLayerMarkerSymbol implements IMarkerSymbol
        # so that the size/offsets/angle are required properties. But they aren't used
        # or exposed anywhere for MultiLayerMarkerSymbol
        _ = stream.read_double('unused marker size')
        _ = stream.read_double('unused marker x/y/offset or angle')
        _ = stream.read_double('unused marker x/y/offset or angle')
        _ = stream.read_double('unused marker x/y/offset or angle')
        _ = stream.read_object('unused color')

        self.halo = stream.read_int() == 1
        self.halo_size = stream.read_double('halo size')

        self.halo_symbol = stream.read_object('halo')

        # useful stuff
        number_layers = stream.read_int('layers')
        for i in range(number_layers):
            layer = stream.read_object('symbol layer {}/{}'.format(i + 1, number_layers))
            self.levels.extend([layer])

        for l in self.levels:
            l.read_enabled(stream)
        for l in self.levels:
            l.read_locked(stream)

        _ = stream.read_double('unknown size')
        _ = stream.read_double('unknown size')

        if version >= 3:
            for l in self.levels:
                l.read_tags(stream)


def read_symbol(_io_stream, debug=False):
    """
    Reads a symbol from the specified file
    """
    stream = Stream(_io_stream, debug)
    try:
        symbol_object = stream.read_object('symbol')
    except InvalidColorException:
        raise UnreadableSymbolException()
    return symbol_object
