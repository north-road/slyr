#!/usr/bin/env python

from struct import unpack
from slyr.parser.stream import Stream

from slyr.parser.objects.line_template import LineTemplate
from slyr.parser.objects.colors import Color
from slyr.parser.objects.decoration import LineDecoration
from slyr.parser.objects.line_symbol_layer import LineSymbolLayer
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


class FillSymbolLayer(SymbolLayer):
    """
    Base class for fill symbol layers
    """

    def __init__(self):
        SymbolLayer.__init__(self)
        self.color = None
        self.outline_layer = None
        self.outline_symbol = None

    @staticmethod
    def create(handle):
        """
        Creates a FillSymbolLayer subclass from the specified file handle
        """
        layer_object = create_object(handle)
        if not issubclass(layer_object.__class__, FillSymbolLayer):
            raise UnreadableSymbolException('Expected FillSymbolLayer, got {}'.format(layer_object))
        return layer_object


class SimpleFillSymbolLayer(FillSymbolLayer):
    """
    Simple fill symbol layer
    """

    def __init__(self):
        FillSymbolLayer.__init__(self)

    def _read(self, stream: Stream):
        # first bit is either an entire LineSymbol or just a LineSymbolLayer
        outline = stream.read_object()
        if outline is not None:
            if issubclass(outline.__class__, SymbolLayer):
                self.outline_layer = outline
            else:
                self.outline_symbol = outline
        if stream.debug:
            print('Finished outline at {}'.format(hex(stream.tell()-1)))

        self.color = stream.read_object()


class MarkerSymbolLayer(SymbolLayer):
    """
    Base class for marker symbol layers
    """

    def __init__(self):
        SymbolLayer.__init__(self)
        self.color = None
        self.outline_layer = None
        self.outline_symbol = None

    @staticmethod
    def create(handle):
        """
        Creates a MarkerSymbolLayer subclass from the specified file handle
        """
        layer_object = create_object(handle)
        if not issubclass(layer_object.__class__, MarkerSymbolLayer):
            raise UnreadableSymbolException('Expected MarkerSymbolLayer, got {}'.format(layer_object))
        return layer_object


class SimpleMarkerSymbolLayer(MarkerSymbolLayer):
    """
    Simple marker symbol layer
    """

    def __init__(self):
        MarkerSymbolLayer.__init__(self)
        self.type = None
        self.size = 0
        self.x_offset = 0
        self.y_offset = 0
        self.outline_enabled = False
        self.outline_color = None
        self.outline_width = 0.0

    def read(self, stream: Stream):
        """
        Reads the symbol layer information. Internally calls _read method
        for individual layer types
        """
        stream.read(self.padding())
        self._read(stream)

        # look for 0d terminator
        while not binascii.hexlify(stream.read(1)) == b'0d':
            pass
        stream.read(15)

        self.x_offset = stream.read_double('x offset')
        self.y_offset = stream.read_double('y offset')

        has_outline = unpack("<B", stream.read(1))[0]
        if has_outline == 1:
            self.outline_enabled = True
        self.outline_width = stream.read_double('outline width')
        self.outline_color = stream.read_object()

        if stream.debug:
            print('finished simple marker layer read at {}'.format(hex(stream.tell())))

        protector = 0
        while not binascii.hexlify(stream.read(1)) == b'ff':
            protector += 1
            if protector > 100:
                raise UnreadableSymbolException('Could not find end point of simple marker')

        stream.read(1)

    def _read(self, stream: Stream):
        self.color = stream.read_object()
        self.size = stream.read_double('size')

        type_code = stream.read_int()
        type_dict = {
            0: 'circle',
            1: 'square',
            2: 'cross',
            3: 'x',
            4: 'diamond'
        }

        if type_code not in type_dict:
            raise UnreadableSymbolException(
                'Unknown marker type at {}, got {}'.format(hex(stream.tell() - 4),
                                                           type_code))
        if stream.debug:
            print('found a {} at {}'.format(type_dict[type_code], hex(stream.tell() - 4)))
        self.type = type_dict[type_code]


class Font:

    def __init__(self):
        self.font = ''

    def read(self, handle):
        handle._io_stream.read(9)
        # repeated font name, not unicode
        skip = unpack(">H", handle._io_stream.read(2))[0]
        if handle.debug:
            print('duplicate font name at {} for {}'.format(hex(handle._io_stream.tell()), skip))
        handle._io_stream.read(skip)


class CharacterMarkerSymbolLayer(MarkerSymbolLayer):
    """
    Character marker symbol layer
    """

    def __init__(self):
        MarkerSymbolLayer.__init__(self)
        self.type = None
        self.size = 0
        self.unicode = 0
        self.x_offset = 0
        self.y_offset = 0
        self.angle = 0
        self.outline_enabled = False
        self.outline_color = None
        self.outline_width = 0.0
        self.font = None

    def terminator(self):
        return None

    def _read(self, stream: Stream):
        if stream.debug:
            print('start character marker at {}'.format(hex(stream.tell())))

        self.color = stream.read_object()

        self.unicode = stream.read_int('unicode')
        self.angle = stream.read_double('angle')
        self.size = stream.read_double('size')
        self.x_offset = stream.read_double('x offset')
        self.y_offset = stream.read_double('y offset')

        # unknown - ends with FFFF
        while not binascii.hexlify(stream.read(2)) == b'ffff':
            stream.rewind(1)

        self.font = stream.read_string('font name')

        # large unknown block
        protector = 0
        while not binascii.hexlify(stream.read(2)) == b'9001':
            stream.rewind(1)
            protector += 1
            if protector > 100:
                raise UnreadableSymbolException('Could not find end point of character marker')
        stream.read(4)
        stream.read(6)

        font = create_object(stream)
        font.read(stream)



class ArrowMarkerSymbolLayer(MarkerSymbolLayer):
    """
    Arrow marker symbol layer
    """

    def __init__(self):
        MarkerSymbolLayer.__init__(self)
        self.type = None
        self.size = 0
        self.width = 0
        self.x_offset = 0
        self.y_offset = 0
        self.angle = 0

    def terminator(self):
        return [b'ffff', b'2440']

    def _read(self, stream: Stream):
        if stream.debug:
            print('start arrow marker at {}'.format(hex(stream.tell())))

        self.color = stream.read_object()

        self.size = stream.read_double('size')
        self.width = stream.read_double('width')
        self.angle = stream.read_double('angle')

        # 12 bytes unknown purpose
        if stream.debug:
            print('skipping 12 unknown bytes at {}'.format(hex(stream.tell())))
        stream.read(12)

        self.x_offset = stream.read_double('x offset')
        self.y_offset = stream.read_double('y offset')


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
            layer = FillSymbolLayer.create(stream)
            if layer:
                layer.read(stream)
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

        unknown_object = create_object(stream)
        if unknown_object is not None:
            assert False, unknown_object
        unknown_size = stream.read_double('unknown size')

        self.color = stream.read_object()

        self.halo = stream.read_int() == 1
        self.halo_size = stream.read_double('halo size')

        self.halo_symbol = create_object(stream)
        if self.halo_symbol is not None:
            self.halo_symbol.read(stream)
        if stream.debug:
            print('finished halo symbol at {}'.format(hex(stream.tell())))

        # not sure about this - there's an extra 02 here if a full fill symbol is used for the halo
        if False and isinstance(self.halo_symbol, Symbol):
            check = binascii.hexlify(stream.read(1))
            if check != b'02':
                raise UnreadableSymbolException('Found unexpected value {} at {}, expected x02'.format(check, hex(stream.tell()-1)))
            stream.read(1)

        if isinstance(self.halo_symbol, SymbolLayer):
            stream.read(4)

#        consume_padding(handle._io_stream)

        # useful stuff
        number_layers = stream.read_int('layers')
        for i in range(number_layers):
            # consume_padding(handle._io_stream)
            layer = MarkerSymbolLayer.create(stream)
            if stream.debug:
                print('marker symbol layer at {}'.format(hex(stream.tell())))

            layer.read(stream)
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


REGISTRY.register('88539431-e06e-11d1-b277-0000f878229e', ArrowMarkerSymbolLayer)
REGISTRY.register('7914e600-c892-11d0-8bb6-080009ee4e41', CharacterMarkerSymbolLayer)
#REGISTRY.register('9a1eba10-cdf9-11d3-81eb-0080c79f0371',DotDensityFillSymbol)
#REGISTRY.register('7914e609-c892-11d0-8bb6-080009ee4e41':GradientFillSymbol)
#REGISTRY.register('7914e5fc-c892-11d0-8bb6-080009ee4e41':GradientFillSymbol)
#REGISTRY.register('7914e606-c892-11d0-8bb6-080009ee4e41':LineFillSymbol)
#REGISTRY.register( '7914e608-c892-11d0-8bb6-080009ee4e41':MarkerFillSymbol)
REGISTRY.register('7914e604-c892-11d0-8bb6-080009ee4e41', FillSymbol)
REGISTRY.register('7914e5fa-c892-11d0-8bb6-080009ee4e41', LineSymbol)
REGISTRY.register('7914e5ff-c892-11d0-8bb6-080009ee4e41', MarkerSymbol),
#REGISTRY.register('d842b082-330c-11d2-9168-0000f87808ee', PictureFillSymbol)
#REGISTRY.register('22c8c5a1-84fc-11d4-834d-0080c79f0371', PictureLineSymbol)
#REGISTRY.register('7914e602-c892-11d0-8bb6-080009ee4e41', PictureMarkerSymbol)
REGISTRY.register('7914e603-c892-11d0-8bb6-080009ee4e41', SimpleFillSymbolLayer)
REGISTRY.register('7914e5fe-c892-11d0-8bb6-080009ee4e41', SimpleMarkerSymbolLayer)

REGISTRY.register('0be35203-8f91-11ce-9de3-00aa004bb851', Font)
