#!/usr/bin/env python

from slyr.parser.stream import Stream
from slyr.parser.object import Object

from slyr.parser.objects.symbol_layer import SymbolLayer

from slyr.parser.exceptions import UnreadableSymbolException
from slyr.parser.color_parser import InvalidColorException
import binascii

"""
Extracts a symbol from a style blob
"""


class Symbol(Object):
    """
    Base class for symbols
    """

    def __init__(self):
        super().__init__()
        self.levels = []

    def _read(self, stream: Stream):
        """
        Should be implemented in subclasses, to handle reading of that particular
        symbol type
        """
        pass

    def read(self, stream: Stream):
        stream.read(10)
        self._read(stream)
        # do we end in 02?
        check = binascii.hexlify(stream.read(1))
        if check != b'02':
            raise UnreadableSymbolException(
                'Found unexpected value {} at {}, expected x02'.format(check, hex(stream.tell() - 1)))
        stream.read(5)

        # PROBLEMATIC!!

        check = binascii.hexlify(stream.read(1))
        if check == b'02':
            stream.read(5)
        else:
            stream.rewind(1)


class LineSymbol(Symbol):
    """
    Line symbol
    """

    def __init__(self):
        super().__init__()

    @staticmethod
    def guid():
        return '7914e5fa-c892-11d0-8bb6-080009ee4e41'

    def _read(self, stream: Stream):
        number_layers = stream.read_uint('layer count')
        for i in range(number_layers):
            layer = stream.read_object('symbol layer {}/{}'.format(i + 1, number_layers))
            self.levels.extend([layer])

        if True:
            # the next section varies in size. To handle this we jump forward to a known anchor
            # point, and then move back by a known amount

            # burn up to the 02
            stream.log('burning up to 02...')
            while not binascii.hexlify(stream.read(1)) == b'02':
                pass

            # jump back a known amount
            stream.rewind(8 * number_layers + 1)

        else:
            stream.read(1)

            stream.read_double('unknown size')
            stream.read_double('unknown size')

        for l in self.levels:
            l.read_enabled(stream)
        for l in self.levels:
            l.read_locked(stream)


class FillSymbol(Symbol):
    """
    Fill symbol
    """

    def __init__(self):
        super().__init__()

    @staticmethod
    def guid():
        return '7914e604-c892-11d0-8bb6-080009ee4e41'

    def _read(self, stream: Stream):
        self.color = stream.read_object('color')

        number_layers = stream.read_int('layers')
        for i in range(number_layers):
            stream.consume_padding()
            layer = stream.read_object('symbol layer')
            self.levels.extend([layer])

        # the next section varies in size. To handle this we jump forward to a known anchor
        # point, and then move back by a known amount

        # burn up to the 02
        stream.log('burning up to 02...')
        while not binascii.hexlify(stream.read(1)) == b'02':
            pass

        # jump back a known amount
        stream.rewind(8 * number_layers + 1)

        for l in self.levels:
            l.read_enabled(stream)
        for l in self.levels:
            l.read_locked(stream)

        # unknown_size = stream.read_double('unknown size')
        # stream.read(2)


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

    def _read(self, stream: Stream):
        # consume section of unknown purpose
        unknown_size = stream.read_double('unknown size')

        unknown_object = stream.read_object('unknown')
        if unknown_object is not None:
            assert False, unknown_object
        unknown_size = stream.read_double('unknown size')

        self.color = stream.read_object('color')

        self.halo = stream.read_int() == 1
        self.halo_size = stream.read_double('halo size')

        self.halo_symbol = stream.read_object('halo')

        # not sure about this - there's an extra 02 here if a full fill symbol is used for the halo
        if False and isinstance(self.halo_symbol, Symbol):
            check = binascii.hexlify(stream.read(1))
            if check != b'02':
                raise UnreadableSymbolException(
                    'Found unexpected value {} at {}, expected x02'.format(check, hex(stream.tell() - 1)))
            stream.read(1)

        if isinstance(self.halo_symbol, SymbolLayer):
            stream.read(4)

        # useful stuff
        number_layers = stream.read_int('layers')
        for i in range(number_layers):
            layer = stream.read_object('layer')
            self.levels.extend([layer])

        for l in self.levels:
            l.read_enabled(stream)
        for l in self.levels:
            l.read_locked(stream)

        unknown_size = stream.read_double('unknown size')
        unknown_size = stream.read_double('unknown size')


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
