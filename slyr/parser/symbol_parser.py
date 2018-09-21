#!/usr/bin/env python

from slyr.parser.stream import Stream

from slyr.parser.objects.line_template import LineTemplate
from slyr.parser.objects.colors import Color
from slyr.parser.objects.decoration import LineDecoration
from slyr.parser.objects.line_symbol_layer import LineSymbolLayer
from slyr.parser.objects.fill_symbol_layer import FillSymbolLayer
from slyr.parser.objects.marker_symbol_layer import MarkerSymbolLayer
from slyr.parser.objects.font import Font

from slyr.parser.objects.symbol_layer import SymbolLayer

from slyr.parser.exceptions import UnreadableSymbolException
from slyr.parser.color_parser import InvalidColorException
from slyr.parser.object_registry import REGISTRY, UnknownGuidException, NotImplementedException
import binascii

"""
Extracts a symbol from a style blob
"""



def create_object(handle):
    """
    Reads an object header and returns the corresponding object class
    """
    if handle.debug:
        print('Reading object header at {}'.format(hex(handle._io_stream.tell())))
    guid_bin = binascii.hexlify(handle._io_stream.read(16))
    guid = REGISTRY.hex_to_guid(guid_bin)
    if handle.debug:
        print('Found guid of {}'.format(guid))

    try:
        res = REGISTRY.create_object(guid)
        if handle.debug:
            print('=={}'.format(res.__class__.__name__))
        return res
    except NotImplementedException as e:
        raise UnreadableSymbolException(e)
    except UnknownGuidException as e:
        raise UnreadableSymbolException(e)


class Symbol:
    """
    Base class for symbols
    """

    def __init__(self):
        self.levels = []

    def _read(self, handle):
        """
        Should be implemented in subclasses, to handle reading of that particular
        symbol type
        """
        pass

    def read(self, handle):
        handle._io_stream.read(10)
        self._read(handle)
        # do we end in 02?
        check = binascii.hexlify(handle._io_stream.read(1))
        if check != b'02':
            raise UnreadableSymbolException(
                'Found unexpected value {} at {}, expected x02'.format(check, hex(handle._io_stream.tell() - 1)))
        handle._io_stream.read(5)

        # PROBLEMATIC!!

        check = binascii.hexlify(handle._io_stream.read(1))
        if check == b'02':
            handle._io_stream.read(5)
        else:
            handle._io_stream.seek(handle._io_stream.tell()-1)


class LineSymbol(Symbol):
    """
    Line symbol
    """

    def __init__(self):
        Symbol.__init__(self)

    def _read(self, stream: Stream):
        number_layers = stream.read_uint('layer count')
        for i in range(number_layers):
            layer = stream.read_object()
            self.levels.extend([layer])

        # the next section varies in size. To handle this we jump forward to a known anchor
        # point, and then move back by a known amount

        # burn up to the 02
        while not binascii.hexlify(stream.read(1)) == b'02':
            pass

        # jump back a known amount
        stream.rewind(8 * number_layers + 1)

        for l in self.levels:
            l.read_enabled(stream)
        for l in self.levels:
            l.read_locked(stream)

        stream.log('')


class FillSymbol(Symbol):
    """
    Fill symbol
    """

    def __init__(self):
        Symbol.__init__(self)

    def _read(self, stream: Stream):
        self.color = stream.read_object()

        number_layers = stream.read_int('layers')
        for i in range(number_layers):
            stream.consume_padding()
            layer = stream.read_object()
            self.levels.extend([layer])

        # the next section varies in size. To handle this we jump forward to a known anchor
        # point, and then move back by a known amount

        # burn up to the 02
        while not binascii.hexlify(stream.read(1)) == b'02':
            pass

        # jump back a known amount
        stream.rewind(8 * number_layers + 1)

        for l in self.levels:
            l.read_enabled(stream)
        for l in self.levels:
            l.read_locked(stream)


class MarkerSymbol(Symbol):
    """
    Marker symbol.

    """

    def __init__(self):
        Symbol.__init__(self)
        self.halo = False
        self.halo_size = 0
        self.halo_symbol = None

    def _read(self, stream: Stream):
        # consume section of unknown purpose
        unknown_size = stream.read_double('unknown size')

        unknown_object = stream.read_object()
        if unknown_object is not None:
            assert False, unknown_object
        unknown_size = stream.read_double('unknown size')

        self.color = stream.read_object()

        self.halo = stream.read_int() == 1
        self.halo_size = stream.read_double('halo size')

        self.halo_symbol = stream.read_object()
        stream.log('finished halo symbol')

        # not sure about this - there's an extra 02 here if a full fill symbol is used for the halo
        if False and isinstance(self.halo_symbol, Symbol):
            check = binascii.hexlify(stream.read(1))
            if check != b'02':
                raise UnreadableSymbolException('Found unexpected value {} at {}, expected x02'.format(check, hex(stream.tell()-1)))
            stream.read(1)

        if isinstance(self.halo_symbol, SymbolLayer):
            stream.read(4)

        # useful stuff
        number_layers = stream.read_int('layers')
        for i in range(number_layers):
            layer = stream.read_object()
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
    handle = Stream(_io_stream, debug)
    symbol_object = create_object(handle)

    try:

        # sometimes symbols are just layers, sometimes whole symbols...
        if issubclass(symbol_object.__class__, SymbolLayer):
            symbol_layer = symbol_object
            symbol_layer.read(handle)
            return symbol_layer
        else:
            if not issubclass(symbol_object.__class__, Symbol):
                raise UnreadableSymbolException('Expected Symbol, got {}'.format(symbol_object))
            symbol = symbol_object
            symbol.read(handle)
            return symbol

    except InvalidColorException:
        raise UnreadableSymbolException()


REGISTRY.register('7914e604-c892-11d0-8bb6-080009ee4e41', FillSymbol)
REGISTRY.register('7914e5fa-c892-11d0-8bb6-080009ee4e41', LineSymbol)
REGISTRY.register('7914e5ff-c892-11d0-8bb6-080009ee4e41', MarkerSymbol),