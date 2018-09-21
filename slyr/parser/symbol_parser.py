#!/usr/bin/env python

from struct import unpack
from slyr.parser.stream import Stream

from slyr.parser.objects.line_template import LineTemplate
from slyr.parser.objects.colors import Color

from slyr.parser.color_parser import InvalidColorException
from slyr.parser.object_registry import REGISTRY, UnknownGuidException, NotImplementedException
import binascii

"""
Extracts a symbol from a style blob
"""


class UnreadableSymbolException(Exception):
    pass


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


class LineDecoration:

    def __init__(self):
        self.decorations = []

    def read(self, handle):
        """
        Reads the decoration information
        """
        handle._io_stream.read(2) # unknown -- maybe includes position as ratio?

        # next bit is probably number of decorations?
        count = unpack("<I", handle._io_stream.read(4))[0]
        if handle.debug:
            print('Count of decorations {} at {}'.format(count,hex(handle._io_stream.tell()-4)))

        for i in range(count):
            decoration = create_object(handle)
            decoration.read(handle)
            self.decorations.append(decoration)


class SimpleLineDecoration:
    """
    ISimpleLineDecorationElement
    """

    def __init__(self):
        super().__init__()
        self.fixed_angle = False
        self.flip_first = False
        self.flip_all = False
        self.marker = None
        self.marker_positions = []

    def read(self, handle):
        """
        Reads the decoration information
        """
        handle._io_stream.read(2) # unknown -- maybe includes position as ratio?

        self.fixed_angle = not bool(unpack("<B", handle._io_stream.read(1))[0])
        if handle.debug:
            print('detected {} at {}'.format('fixed angle' if self.fixed_angle else 'not fixed angle',
                                             hex(handle._io_stream.tell() - 1)))
        self.flip_first = bool(unpack("<B", handle._io_stream.read(1))[0])
        if handle.debug:
            print('detected {} at {}'.format('flip first' if self.flip_first else 'no flip first',
                                             hex(handle._io_stream.tell() - 1)))
        self.flip_all = bool(unpack("<B", handle._io_stream.read(1))[0])
        if handle.debug:
            print('detected {} at {}'.format('flip all' if self.flip_all else 'no flip all',
                                             hex(handle._io_stream.tell() - 1)))

        handle._io_stream.read(2) # unknown -- maybe includes position as ratio?

        self.marker = create_object(handle)
        self.marker.read(handle)

        if False and not issubclass(self.marker.__class__, SymbolLayer):
            # TODO ewwwwww
            while not binascii.hexlify(handle._io_stream.read(1)) == b'02':
                pass
            while not binascii.hexlify(handle._io_stream.read(1)) == b'02':
                pass
            handle._io_stream.read(5)

        # next bit is the number of doubles coming next
        marker_number_positions = unpack("<L", handle._io_stream.read(4))[0]
        if handle.debug:
            print('detected {} marker positions at {}'.format(marker_number_positions,
                                                              hex(handle._io_stream.tell() - 4)))

        # next bit is the positions themselves -- maybe we can infer this from the number of positions
        # alone. E.g. 2 positions = 0, 1. 3 positions = 0, 0.5, 1
        for i in range(marker_number_positions):
            self.marker_positions.append(unpack("<d", handle._io_stream.read(8))[0])
        if handle.debug:
            print('marker positions are {}'.format(self.marker_positions))
            print('ended decoration at {}'.format(hex(handle._io_stream.tell() - 1)))


class SymbolLayer:
    """
    Base class for symbol layers
    """

    def __init__(self):
        self.locked = False
        self.enabled = True

    def padding(self):
        return 2

    def read_enabled(self, handle):
        """
        Reads the layer 'enabled' state
        """
        enabled = unpack("<I", handle._io_stream.read(4))[0]
        self.enabled = enabled == 1
        if handle.debug:
            print('read enabled ({}) at {} '.format(self.enabled, hex(handle._io_stream.tell() - 4)))

    def read_locked(self, handle):
        """
        Reads the layer 'locked' state

        """
        locked = unpack("<I", handle._io_stream.read(4))[0]
        self.locked = locked == 1
        if handle.debug:
            print('read layer locked ({}) at {} '.format(self.locked, hex(handle._io_stream.tell() - 4)))

    def _read(self, handle):
        """
        Should be implemented in subclasses, to handle reading of that particular
        symbol layer type
        """
        pass

    def terminator(self):
        """
        Returns the symbol layer terminator, if present
        """
        return [b'0d00000000000000']

    def read(self, handle):
        """
        Reads the symbol layer information. Internally calls _read method
        for individual layer types
        """
        if handle.debug:
            print('skipping padding of {} at {}'.format(self.padding(), hex(handle._io_stream.tell())))
        handle._io_stream.read(self.padding())

        self._read(handle)

        # look for 0d terminator
        if self.terminator() is not None:
            if handle.debug:
                print('looking for {} from {}'.format(self.terminator(), hex(handle._io_stream.tell())))

            terminator_len = int(len(self.terminator()[0]) / 2)
            while True:
                start = handle._io_stream.tell()
                if binascii.hexlify(handle._io_stream.read(terminator_len)) in self.terminator():
                    break
                handle._io_stream.seek(start + 1)

        if handle.debug:
            print('finished layer read at {}'.format(hex(handle._io_stream.tell())))


class LineSymbolLayer(SymbolLayer):
    """
    Base class for line symbol layers
    """

    def __init__(self):
        SymbolLayer.__init__(self)
        self.color = None

    @staticmethod
    def create(handle):
        """
        Creates a LineSymbolLayer subclass from the specified file handle
        """
        layer_object = create_object(handle)
        if not issubclass(layer_object.__class__, LineSymbolLayer) \
                and not issubclass(layer_object.__class__, LineSymbol):
            raise UnreadableSymbolException('Expected LineSymbolLayer or LineSymbol, got {}'.format(layer_object))
        return layer_object

    @staticmethod
    def read_cap(_io_stream):
        cap_bin = unpack("<B", _io_stream.read(1))[0]
        if cap_bin == 0:
            return 'butt'
        elif cap_bin == 1:
            return 'round'
        elif cap_bin == 2:
            return 'square'
        else:
            raise UnreadableSymbolException('unknown cap style {}'.format(cap_bin))

    @staticmethod
    def read_join(_io_stream):
        join_bin = unpack("<B", _io_stream.read(1))[0]
        if join_bin == 0:
            return 'miter'
        elif join_bin == 1:
            return 'round'
        elif join_bin == 2:
            return 'bevel'
        else:
            raise UnreadableSymbolException('unknown join style {}'.format(join_bin))

    @staticmethod
    def read_end_markers(handle):
        line_decoration = create_object(handle)
        line_decoration.read(handle)
        return line_decoration


class SimpleLineSymbolLayer(LineSymbolLayer):
    """
    Simple line symbol layer
    """

    def __init__(self):
        LineSymbolLayer.__init__(self)
        self.width = None
        self.line_type = None

    def _read(self, stream: Stream):
        self.color = stream.read_object()
        self.width = stream.read_double('width')
        self.line_type = LineSymbol.read_line_type(stream._io_stream)
        if stream.debug:
            print('read line type of {} at {}'.format(self.line_type, hex(stream.tell() - 4)))


class CartographicLineSymbolLayer(LineSymbolLayer):
    """
    Cartographic line symbol layer
    """

    def __init__(self):
        LineSymbolLayer.__init__(self)
        self.width = None
        self.cap = None
        self.join = None
        self.offset = None
        self.template = None
        self.decoration = None

    def padding(self):
        return 2

    def _read(self, stream: Stream):
        self.cap = self.read_cap(stream._io_stream)

        unknown = binascii.hexlify(stream.read(3))
        if unknown != b'000000':
            raise UnreadableSymbolException('Differing unknown string {}'.format(unknown))
        self.join = self.read_join(stream._io_stream)
        unknown = binascii.hexlify(stream.read(3))
        if unknown != b'000000':
            raise UnreadableSymbolException('Differing unknown string {}'.format(unknown))

        self.width = stream.read_double('width')

        unknown = binascii.hexlify(stream.read(1))
        if unknown != b'00':
            raise UnreadableSymbolException('Differing unknown byte')

        self.offset = stream.read_double('offset')
        self.color = stream.read_object()
        self.template = stream.read_object()

        # check for markers
        start = stream.tell()
        if stream.debug:
            print('scanning for end markers from {}'.format(hex(start)))

        self.decoration = create_object(stream)
        if self.decoration is not None:
            self.decoration.read(stream)


class MarkerLineSymbolLayer(LineSymbolLayer):
    """
    Marker line symbol layer
    """

    def __init__(self):
        LineSymbolLayer.__init__(self)
        self.cap = None
        self.join = None
        self.offset = None
        self.pattern_interval = 0
        self.pattern_parts = []
        self.pattern_marker = None
        self.marker = None
        self.marker_fixed_angle = False
        self.marker_flip_first = False
        self.marker_flip_all = False
        self.marker_positions = []

    def padding(self):
        return 2

    def _read(self, handle):
        self.cap = self.read_cap(handle._io_stream)
        if handle.debug:
            print('read cap of {} at {}'.format(self.cap, hex(handle._io_stream.tell() - 1)))

        self.offset = unpack("<d", handle._io_stream.read(8))[0]
        if handle.debug:
            print('read offset of {} at {}'.format(self.offset, hex(handle._io_stream.tell() - 8)))

        self.pattern_marker = create_object(handle)
        self.pattern_marker.read(handle)
        if handle.debug:
            print('back at marker line at {}'.format(hex(handle._io_stream.tell())))

        if False and not issubclass(self.pattern_marker.__class__, SymbolLayer):
            # ewwwwww
            while not binascii.hexlify(handle._io_stream.read(1)) == b'02':
                pass
            while not binascii.hexlify(handle._io_stream.read(1)) == b'02':
                pass
            handle._io_stream.read(5)

        handle._io_stream.read(18)
        self.pattern_interval = unpack("<d", handle._io_stream.read(8))[0]
        if handle.debug:
            print('read interval of {} at {}'.format(self.pattern_interval, hex(handle._io_stream.tell() - 8)))

        # symbol pattern
        pattern_part_count = unpack("<L", handle._io_stream.read(4))[0]
        if handle.debug:
            print('pattern has {} parts at {}'.format(pattern_part_count, hex(handle._io_stream.tell() - 4)))

        self.pattern_parts = []
        for p in range(pattern_part_count):
            filled_squares = unpack("<d", handle._io_stream.read(8))[0]
            empty_squares = unpack("<d", handle._io_stream.read(8))[0]
            self.pattern_parts.append([filled_squares, empty_squares])

        if handle.debug:
            print('deciphered marker line pattern ending at {}'.format(hex(handle._io_stream.tell())))
            pattern = ''
            for p in self.pattern_parts:
                pattern += '-' * int(p[0]) + '.' * int(p[1])
            print(pattern)

        if binascii.hexlify(handle._io_stream.read(1)) == b'f5':
            if handle.debug:
                print('detected end markers at {}'.format(hex(handle._io_stream.tell() - 1)))
            end_markers = self.read_end_markers(handle)
            self.marker_fixed_angle = end_markers['marker_fixed_angle']
            self.marker_flip_first = end_markers['marker_flip_first']
            self.marker_flip_all = end_markers['marker_flip_all']
            self.marker = end_markers['marker']
            self.marker_positions = end_markers['marker_positions']


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
        outline = create_object(stream)
        if outline is not None:
            if stream.debug:
                print('starting outline symbol at {}'.format(hex(stream.tell())))
            outline.read(stream)

            if issubclass(outline.__class__, SymbolLayer):
                self.outline_layer = outline
            else:
                self.outline_symbol = outline
        if stream.debug:
            print('Finished outline at {}'.format(hex(stream.tell()-1)))
        #consume_padding(handle._io_stream)

       # unknown = unpack("<L", handle._io_stream.read(4))[0]

        # sometimes an extra 02 terminator here
        #start = handle._io_stream.tell()
        #symbol_terminator = binascii.hexlify(handle._io_stream.read(1))
        #if symbol_terminator == b'02':
        #    consume_padding(handle._io_stream)
        #else:
        #    handle._io_stream.seek(start)

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

    def _read(self, handle):
        number_layers = unpack("<L", handle._io_stream.read(4))[0]
        if handle.debug:
            print('detected {} layers at {}'.format(number_layers, hex(handle._io_stream.tell() - 4)))

        for i in range(number_layers):
            layer = LineSymbolLayer.create(handle)
            if layer:
                layer.read(handle)
            self.levels.extend([layer])

        # the next section varies in size. To handle this we jump forward to a known anchor
        # point, and then move back by a known amount

        # burn up to the 02
        while not binascii.hexlify(handle._io_stream.read(1)) == b'02':
            pass

        # jump back a known amount
        handle._io_stream.seek(handle._io_stream.tell() - 8 * number_layers - 1)

        for l in self.levels:
            l.read_enabled(handle)
        for l in self.levels:
            l.read_locked(handle)

        if handle.debug:
            print('at {}'.format(hex(handle._io_stream.tell())))

 #       while not binascii.hexlify(handle._io_stream.read(1)) == b'02':
  #          pass

    @staticmethod
    def read_line_type(_io_stream):
        """
        Interprets the line type bytes
        """
        line_type = unpack("<I", _io_stream.read(4))[0]
        types = {0: 'solid',
                 1: 'dashed',
                 2: 'dotted',
                 3: 'dash dot',
                 4: 'dash dot dot',
                 5: 'null'
                 }
        if line_type not in types:
            raise UnreadableSymbolException('unknown line type {} at {}'.format(line_type, hex(_io_stream.tell() - 4)))
        return types[line_type]


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
REGISTRY.register('7914e5fb-c892-11d0-8bb6-080009ee4e41', CartographicLineSymbolLayer)
REGISTRY.register('7914e600-c892-11d0-8bb6-080009ee4e41', CharacterMarkerSymbolLayer)
#REGISTRY.register('9a1eba10-cdf9-11d3-81eb-0080c79f0371',DotDensityFillSymbol)
#REGISTRY.register('7914e609-c892-11d0-8bb6-080009ee4e41':GradientFillSymbol)
#REGISTRY.register('7914e5fc-c892-11d0-8bb6-080009ee4e41':GradientFillSymbol)
#REGISTRY.register('7914e606-c892-11d0-8bb6-080009ee4e41':LineFillSymbol)
#REGISTRY.register( '7914e608-c892-11d0-8bb6-080009ee4e41':MarkerFillSymbol)
REGISTRY.register('7914e5fd-c892-11d0-8bb6-080009ee4e41', MarkerLineSymbolLayer)
REGISTRY.register('7914e604-c892-11d0-8bb6-080009ee4e41', FillSymbol)
REGISTRY.register('7914e5fa-c892-11d0-8bb6-080009ee4e41', LineSymbol)
REGISTRY.register('7914e5ff-c892-11d0-8bb6-080009ee4e41', MarkerSymbol),
#REGISTRY.register('d842b082-330c-11d2-9168-0000f87808ee', PictureFillSymbol)
#REGISTRY.register('22c8c5a1-84fc-11d4-834d-0080c79f0371', PictureLineSymbol)
#REGISTRY.register('7914e602-c892-11d0-8bb6-080009ee4e41', PictureMarkerSymbol)
REGISTRY.register('7914e603-c892-11d0-8bb6-080009ee4e41', SimpleFillSymbolLayer)
REGISTRY.register('7914e5f9-c892-11d0-8bb6-080009ee4e41', SimpleLineSymbolLayer)
REGISTRY.register('7914e5fe-c892-11d0-8bb6-080009ee4e41', SimpleMarkerSymbolLayer)
REGISTRY.register('533d88f5-0a1a-11d2-b27f-0000f878229e', LineDecoration)
REGISTRY.register('533d88f3-0a1a-11d2-b27f-0000f878229e', SimpleLineDecoration)

REGISTRY.register('0be35203-8f91-11ce-9de3-00aa004bb851', Font)
