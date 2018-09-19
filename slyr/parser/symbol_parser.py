#!/usr/bin/env python

from struct import unpack
from slyr.parser.color_parser import (read_color_and_model,
                                      InvalidColorException)
import binascii

"""
Extracts a symbol from a style blob
"""


class UnreadableSymbolException(Exception):
    pass


class Handle:
    """
    Holds file handle and other useful things while parsing the symbol blob
    """

    def __init__(self, file_handle, debug=False):
        self.file_handle = file_handle
        self.debug = debug


def read_string(handle):
    """
    Decodes a string from the binary

    From the .dot BinaryWriter code: 'This method first writes the length of the string as
    a four-byte unsigned integer, and then writes that many characters
    to the stream'
    """
    start = handle.file_handle.tell()
    length = unpack("<I", handle.file_handle.read(4))[0]
    if handle.debug:
        print('string of length {} at {}'.format(length, hex(start)))
    buffer = handle.file_handle.read(length)
    string = buffer.decode('utf-16')
    if handle.debug:
        print('found string "{}" at {}'.format(string, hex(start)))
    return string[:-1]


def read_object_header(handle):
    """
    Reads and interprets the header for a new object block. Returns the object type
    code (2 bytes)
    """
    if handle.debug:
        print('Reading object header at {}'.format(hex(handle.file_handle.tell())))
    object_type = binascii.hexlify(handle.file_handle.read(2))

    # hack - but doesn't seem needed anymore?!
    # if object_type[2:] == b'40':
    # object_type = binascii.hexlify(handle.file_handle.read(2))

    if object_type == b'e614':
        # second chance, since some overzealous padding consumer may have eaten
        # the start of a "00e6" Character Marker Symbol
        handle.file_handle.seek(handle.file_handle.tell() - 3)
        object_type = binascii.hexlify(handle.file_handle.read(2))

    # Some magic sequence of unknown origin:
    magic_1 = binascii.hexlify(handle.file_handle.read(14))
    if magic_1 != b'147992c8d0118bb6080009ee4e41' and magic_1 != b'53886ee0d111b2770000f878229e':
        raise UnreadableSymbolException('Differing object header at {}, got {}'.format(
            hex(handle.file_handle.tell() - 16), magic_1))

    return object_type

    # Some padding bytes of unknown purpose
    # Encountered values are:
    #  010001
    #  02000dxxxxxxxxxxxxxx
    #  1000000001000, 110000001000,... (in lyr files)
    skip_bytes = unpack("<H", handle.file_handle.read(2))[0]
    if skip_bytes == 1:
        pass
    elif skip_bytes in (2, 3, 4):
        if binascii.hexlify(handle.file_handle.read(1)) == b'0d':
            handle.file_handle.read(7)
        else:
            handle.file_handle.seek(handle.file_handle.tell() - 1)
    # experimental! - might be safer to assert False here. Only encountered in .lyr fails so far
    else:
        handle.file_handle.read(4)

    return object_type


def create_object(handle):
    """
    Reads an object header and returns the corresponding object class
    """
    start = handle.file_handle.tell()
    object_code = read_object_header(handle)
    object_dict = {
        b'04e6': FillSymbol,
        b'ffe5': MarkerSymbol,
        b'fae5': LineSymbol,
        b'f9e5': SimpleLineSymbolLayer,
        b'fbe5': CartographicLineSymbolLayer,
        b'03e6': SimpleFillSymbolLayer,
        b'fee5': SimpleMarkerSymbolLayer,
        b'00e6': CharacterMarkerSymbolLayer,
        b'3194': ArrowMarkerSymbolLayer,
        #  '02e6': PictureMarkerSymbolLayer
    }

    if object_code not in object_dict:
        raise UnreadableSymbolException('Unknown object code at {}, got {}'.format(hex(start), object_code))

    if handle.debug:
        print('found a {} at {}'.format(object_dict[object_code], hex(start)))
    return object_dict[object_code]


def read_magic_2(handle):
    """
    Consumes an expected magic sequence (2), of unknown purpose
    """
    magic_2 = binascii.hexlify(handle.file_handle.read(15))
    if magic_2 != b'c4e97e23d1d0118383080009b996cc':
        raise UnreadableSymbolException('Differing magic string 2: {}'.format(magic_2))

    terminator = binascii.hexlify(handle.file_handle.read(2))
    if not terminator == b'0100':
        # .lyr files have an extra 4 bytes in here - of unknown purpose
        handle.file_handle.read(4)

    start = handle.file_handle.tell()
    terminator = binascii.hexlify(handle.file_handle.read(1))
    if terminator != b'01':
        raise UnreadableSymbolException('Expected 01 at {}, got {}'.format(hex(start), terminator))
    if handle.debug:
        print('finished magic 2 at {}'.format(hex(handle.file_handle.tell() - 1)))


def read_magic_3(handle):
    """
    Consumes an expected magic sequence (3), of unknown purpose
    """
    magic_3 = binascii.hexlify(handle.file_handle.read(17))
    if magic_3 != b'883d531a0ad211b27f0000f878229e0100':
        raise UnreadableSymbolException(
            'Differing magic string 3: {} at {}'.format(magic_3, hex(handle.file_handle.tell() - 17)))

    if handle.debug:
        print('finished magic 3 at {}'.format(hex(handle.file_handle.tell() - 1)))


def consume_padding(file_handle):
    """
    Swallows up '00' padding from a file handle.

    Use with caution! This is fragile if a possible valid '00' byte follows the padding.
    """
    last_position = file_handle.tell()
    while binascii.hexlify(file_handle.read(1)) == b'00':
        last_position = file_handle.tell()
    file_handle.seek(last_position)


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
        enabled = unpack("<I", handle.file_handle.read(4))[0]
        self.enabled = enabled == 1
        if handle.debug:
            print('read enabled ({}) at {} '.format(self.enabled, hex(handle.file_handle.tell() - 4)))

    def read_locked(self, handle):
        """
        Reads the layer 'locked' state

        """
        locked = unpack("<I", handle.file_handle.read(4))[0]
        self.locked = locked == 1
        if handle.debug:
            print('read layer locked ({}) at {} '.format(self.locked, hex(handle.file_handle.tell() - 4)))

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
        return [b'0d']

    def read(self, handle):
        """
        Reads the symbol layer information. Internally calls _read method
        for individual layer types
        """
        if handle.debug:
            print('skipping padding of {} at {}'.format(self.padding(), hex(handle.file_handle.tell())))
        handle.file_handle.read(self.padding())

        self._read(handle)

        # look for 0d terminator
        if self.terminator() is not None:
            if handle.debug:
                print('looking for {} from {}'.format(self.terminator(), hex(handle.file_handle.tell())))

            terminator_len = int(len(self.terminator()[0]) / 2)
            while True:
                start = handle.file_handle.tell()
                if binascii.hexlify(handle.file_handle.read(terminator_len)) in self.terminator():
                    break
                handle.file_handle.seek(start + 1)

        if handle.debug:
            print('finished layer read at {}'.format(hex(handle.file_handle.tell())))


class LineSymbolLayer(SymbolLayer):
    """
    Base class for line symbol layers
    """

    def __init__(self):
        SymbolLayer.__init__(self)
        self.color_model = None
        self.color = None

    @staticmethod
    def create(handle):
        """
        Creates a LineSymbolLayer subclass from the specified file handle
        """
        layer_object = create_object(handle)
        if not issubclass(layer_object, LineSymbolLayer) \
                and not issubclass(layer_object, LineSymbol):
            raise UnreadableSymbolException('Expected LineSymbolLayer or LineSymbol, got {}'.format(layer_object))
        return layer_object()


class SimpleLineSymbolLayer(LineSymbolLayer):
    """
    Simple line symbol layer
    """

    def __init__(self):
        LineSymbolLayer.__init__(self)
        self.width = None
        self.line_type = None

    def _read(self, handle):
        self.color_model, self.color = read_color_and_model(handle.file_handle, debug=handle.debug)
        self.width = unpack("<d", handle.file_handle.read(8))[0]
        if handle.debug:
            print('read width of {} at {}'.format(self.width, hex(handle.file_handle.tell() - 8)))
        self.line_type = LineSymbol.read_line_type(handle.file_handle)
        if handle.debug:
            print('read line type of {} at {}'.format(self.line_type, hex(handle.file_handle.tell() - 4)))


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
        self.pattern_interval = 0
        self.pattern_parts = []
        self.marker = None
        self.marker_fixed_angle = False
        self.marker_flip_first = False
        self.marker_flip_all = False
        self.marker_positions = []

    def padding(self):
        return 2

    def read_cap(self, file_handle):
        cap_bin = unpack("<B", file_handle.read(1))[0]
        if cap_bin == 0:
            self.cap = 'butt'
        elif cap_bin == 1:
            self.cap = 'round'
        elif cap_bin == 2:
            self.cap = 'square'
        else:
            raise UnreadableSymbolException('unknown cap style {}'.format(cap_bin))

    def read_join(self, file_handle):
        join_bin = unpack("<B", file_handle.read(1))[0]
        if join_bin == 0:
            self.join = 'miter'
        elif join_bin == 1:
            self.join = 'round'
        elif join_bin == 2:
            self.join = 'bevel'
        else:
            raise UnreadableSymbolException('unknown join style {}'.format(join_bin))

    def _read(self, handle):
        self.read_cap(handle.file_handle)

        unknown = binascii.hexlify(handle.file_handle.read(3))
        if unknown != b'000000':
            raise UnreadableSymbolException('Differing unknown string {}'.format(unknown))
        self.read_join(handle.file_handle)
        unknown = binascii.hexlify(handle.file_handle.read(3))
        if unknown != b'000000':
            raise UnreadableSymbolException('Differing unknown string {}'.format(unknown))

        self.width = unpack("<d", handle.file_handle.read(8))[0]
        if handle.debug:
            print('read width of {} at {}'.format(self.width, hex(handle.file_handle.tell() - 8)))

        unknown = binascii.hexlify(handle.file_handle.read(1))
        if unknown != b'00':
            raise UnreadableSymbolException('Differing unknown byte')

        self.offset = unpack("<d", handle.file_handle.read(8))[0]
        self.color_model, self.color = read_color_and_model(handle.file_handle, debug=handle.debug)

        # 18 unknown bytes
        binascii.hexlify(handle.file_handle.read(18))

        self.pattern_interval = unpack("<d", handle.file_handle.read(8))[0]
        if handle.debug:
            print('read interval of {} at {}'.format(self.pattern_interval, hex(handle.file_handle.tell() - 8)))

        # symbol pattern
        pattern_part_count = unpack("<L", handle.file_handle.read(4))[0]
        if handle.debug:
            print('pattern has {} parts at {}'.format(pattern_part_count, hex(handle.file_handle.tell() - 4)))

        self.pattern_parts = []
        for p in range(pattern_part_count):
            filled_squares = unpack("<d", handle.file_handle.read(8))[0]
            empty_squares = unpack("<d", handle.file_handle.read(8))[0]
            self.pattern_parts.append([filled_squares, empty_squares])

        if handle.debug:
            print('deciphered cartographic line pattern ending at {}'.format(hex(handle.file_handle.tell())))
            pattern = ''
            for p in self.pattern_parts:
                pattern += '-' * int(p[0]) + '.' * int(p[1])
            print(pattern)

        # check for markers
        start = handle.file_handle.tell()
        if handle.debug:
            print('scanning for end markers from {}'.format(hex(start)))

        if binascii.hexlify(handle.file_handle.read(1)) == b'f5':
            if handle.debug:
                print('detected end markers at {}'.format(hex(handle.file_handle.tell() - 1)))
            read_magic_3(handle)

            unknown = unpack("<L", handle.file_handle.read(4))[0]
            if handle.debug:
                print('read unknown int of {} at {}'.format(unknown, hex(handle.file_handle.tell() - 4)))

            handle.file_handle.read(1)

            read_magic_3(handle)
            self.marker_fixed_angle = not bool(unpack("<B", handle.file_handle.read(1))[0])
            if handle.debug:
                print('detected {} at {}'.format('fixed angle' if self.marker_fixed_angle else 'not fixed angle',
                                                 hex(handle.file_handle.tell() - 1)))
            self.marker_flip_first = bool(unpack("<B", handle.file_handle.read(1))[0])
            if handle.debug:
                print('detected {} at {}'.format('flip first' if self.marker_flip_first else 'no flip first',
                                                 hex(handle.file_handle.tell() - 1)))
            self.marker_flip_all = bool(unpack("<B", handle.file_handle.read(1))[0])
            if handle.debug:
                print('detected {} at {}'.format('flip all' if self.marker_flip_all else 'no flip all',
                                                 hex(handle.file_handle.tell() - 1)))

            handle.file_handle.read(2)
            self.marker = create_object(handle)()
            self.marker.read(handle)

            if issubclass(self.marker.__class__, SymbolLayer):
                unknown = binascii.hexlify(handle.file_handle.read(2))
                if unknown != b'ffff':
                    raise UnreadableSymbolException(
                        'Differing unknown byte at {}'.format(hex(handle.file_handle.tell() - 2)))
            else:
                # ewwwwww
                while not binascii.hexlify(handle.file_handle.read(1)) == b'02':
                    pass
                while not binascii.hexlify(handle.file_handle.read(1)) == b'02':
                    pass
                handle.file_handle.read(5)

            # next bit is the number of doubles coming next
            marker_number_positions = unpack("<L", handle.file_handle.read(4))[0]
            if handle.debug:
                print('detected {} marker positions at {}'.format(marker_number_positions,
                                                                  hex(handle.file_handle.tell() - 4)))

            # next bit is the positions themselves -- maybe we can infer this from the number of positions
            # alone. E.g. 2 positions = 0, 1. 3 positions = 0, 0.5, 1
            for i in range(marker_number_positions):
                self.marker_positions.append(unpack("<d", handle.file_handle.read(8))[0])
            if handle.debug:
                print('marker positions are {}'.format(self.marker_positions))
                print('ended carto marker at {}'.format(hex(handle.file_handle.tell() - 1)))


class FillSymbolLayer(SymbolLayer):
    """
    Base class for fill symbol layers
    """

    def __init__(self):
        SymbolLayer.__init__(self)
        self.color_model = None
        self.color = None
        self.outline_layer = None
        self.outline_symbol = None

    @staticmethod
    def create(handle):
        """
        Creates a FillSymbolLayer subclass from the specified file handle
        """
        layer_object = create_object(handle)
        if not issubclass(layer_object, FillSymbolLayer):
            raise UnreadableSymbolException('Expected FillSymbolLayer, got {}'.format(layer_object))
        return layer_object()


class SimpleFillSymbolLayer(FillSymbolLayer):
    """
    Simple fill symbol layer
    """

    def __init__(self):
        FillSymbolLayer.__init__(self)

    def _read(self, handle):
        # first bit is either an entire LineSymbol or just a LineSymbolLayer
        outline = LineSymbolLayer.create(handle)
        if isinstance(outline, LineSymbol):
            # embedded outline symbol line
            self.outline_symbol = outline
            if handle.debug:
                print('starting outline symbol at {}'.format(hex(handle.file_handle.tell())))
            self.outline_symbol.read(handle)
        else:
            self.outline_layer = outline
            self.outline_layer.read(handle)

        consume_padding(handle.file_handle)

        # sometimes an extra 02 terminator here
        start = handle.file_handle.tell()
        symbol_terminator = binascii.hexlify(handle.file_handle.read(1))
        if symbol_terminator == b'02':
            consume_padding(handle.file_handle)
        else:
            handle.file_handle.seek(start)

        self.color_model, self.color = read_color_and_model(handle.file_handle, handle.debug)


class MarkerSymbolLayer(SymbolLayer):
    """
    Base class for marker symbol layers
    """

    def __init__(self):
        SymbolLayer.__init__(self)
        self.color_model = None
        self.color = None
        self.outline_layer = None
        self.outline_symbol = None

    @staticmethod
    def create(handle):
        """
        Creates a MarkerSymbolLayer subclass from the specified file handle
        """
        layer_object = create_object(handle)
        if not issubclass(layer_object, MarkerSymbolLayer):
            raise UnreadableSymbolException('Expected MarkerSymbolLayer, got {}'.format(layer_object))
        return layer_object()


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
        self.outline_color_model = None

    def read(self, handle):
        """
        Reads the symbol layer information. Internally calls _read method
        for individual layer types
        """
        handle.file_handle.read(self.padding())
        self._read(handle)

        # look for 0d terminator
        while not binascii.hexlify(handle.file_handle.read(1)) == b'0d':
            pass

        handle.file_handle.read(15)
        if handle.debug:
            print('xy offset at {}'.format(hex(handle.file_handle.tell())))
        self.x_offset = unpack("<d", handle.file_handle.read(8))[0]
        self.y_offset = unpack("<d", handle.file_handle.read(8))[0]

        has_outline = unpack("<B", handle.file_handle.read(1))[0]
        if has_outline == 1:
            self.outline_enabled = True
        self.outline_width = unpack("<d", handle.file_handle.read(8))[0]
        self.outline_color_model, self.outline_color = read_color_and_model(handle.file_handle, debug=handle.debug)

        if handle.debug:
            print('finished simple marker layer read at {}'.format(hex(handle.file_handle.tell())))

        protector = 0
        while not binascii.hexlify(handle.file_handle.read(1)) == b'ff':
            protector += 1
            if protector > 100:
                raise UnreadableSymbolException('Could not find end point of simple marker')

        handle.file_handle.read(1)

    def _read(self, handle):
        self.color_model, self.color = read_color_and_model(handle.file_handle, debug=handle.debug)
        self.size = unpack("<d", handle.file_handle.read(8))[0]

        type_code = unpack("<L", handle.file_handle.read(4))[0]
        type_dict = {
            0: 'circle',
            1: 'square',
            2: 'cross',
            3: 'x',
            4: 'diamond'
        }

        if type_code not in type_dict:
            raise UnreadableSymbolException(
                'Unknown marker type at {}, got {}'.format(hex(handle.file_handle.tell() - 4),
                                                           type_code))
        if handle.debug:
            print('found a {} at {}'.format(type_dict[type_code], hex(handle.file_handle.tell() - 4)))
        self.type = type_dict[type_code]


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
        self.outline_color_model = None
        self.font = None

    def terminator(self):
        return [b'b851']

    def _read(self, handle):
        if handle.debug:
            print('start character marker at {}'.format(hex(handle.file_handle.tell())))

        self.color_model, self.color = read_color_and_model(handle.file_handle, debug=handle.debug)

        self.unicode = unpack("<L", handle.file_handle.read(4))[0]
        if handle.debug:
            print('unicode of {} at {}'.format(self.unicode, hex(handle.file_handle.tell() - 4)))

        self.angle = unpack("<d", handle.file_handle.read(8))[0]
        self.size = unpack("<d", handle.file_handle.read(8))[0]
        if handle.debug:
            print('size of {} at {}'.format(self.size, hex(handle.file_handle.tell() - 8)))
        self.x_offset = unpack("<d", handle.file_handle.read(8))[0]
        self.y_offset = unpack("<d", handle.file_handle.read(8))[0]

        # unknown - ends with FFFF
        while not binascii.hexlify(handle.file_handle.read(2)) == b'ffff':
            handle.file_handle.seek(handle.file_handle.tell() - 1)

        if handle.debug:
            print('start font name at {}'.format(hex(handle.file_handle.tell())))
        self.font = read_string(handle)

        # large unknown block
        protector = 0
        while not binascii.hexlify(handle.file_handle.read(2)) == b'9001':
            handle.file_handle.seek(handle.file_handle.tell() - 1)
            protector += 1
            if protector > 100:
                raise UnreadableSymbolException('Could not find end point of character marker')
        handle.file_handle.read(3)

        # repeated font name, not unicode
        skip = unpack(">h", handle.file_handle.read(2))[0]
        if handle.debug:
            print('duplicate font name at {} for {}'.format(hex(handle.file_handle.tell()), skip))
        handle.file_handle.read(skip)


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

    def _read(self, handle):
        if handle.debug:
            print('start arrow marker at {}'.format(hex(handle.file_handle.tell())))

        self.color_model, self.color = read_color_and_model(handle.file_handle, debug=handle.debug)

        self.size = unpack("<d", handle.file_handle.read(8))[0]
        if handle.debug:
            print('size of {} at {}'.format(self.size, hex(handle.file_handle.tell() - 8)))
        self.width = unpack("<d", handle.file_handle.read(8))[0]
        if handle.debug:
            print('width of {} at {}'.format(self.width, hex(handle.file_handle.tell() - 8)))
        self.angle = unpack("<d", handle.file_handle.read(8))[0]
        if handle.debug:
            print('angle of {} at {}'.format(self.angle, hex(handle.file_handle.tell() - 8)))

        # 12 bytes unknown purpose
        if handle.debug:
            print('skipping 12 unknown bytes at {}'.format(hex(handle.file_handle.tell())))
        handle.file_handle.read(12)

        self.x_offset = unpack("<d", handle.file_handle.read(8))[0]
        if handle.debug:
            print('x offset of {} at {}'.format(self.x_offset, hex(handle.file_handle.tell() - 8)))
        self.y_offset = unpack("<d", handle.file_handle.read(8))[0]
        if handle.debug:
            print('y offset of {} at {}'.format(self.y_offset, hex(handle.file_handle.tell() - 8)))


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
        handle.file_handle.read(self.padding())
        #        consume_padding(handle.file_handle)
        self._read(handle)

    def padding(self):
        return 0


class LineSymbol(Symbol):
    """
    Line symbol
    """

    def __init__(self):
        Symbol.__init__(self)

    def padding(self):
        return 10

    def _read(self, handle):
        number_layers = unpack("<L", handle.file_handle.read(4))[0]
        if handle.debug:
            print('detected {} layers at {}'.format(number_layers, hex(handle.file_handle.tell() - 4)))

        for i in range(number_layers):
            consume_padding(handle.file_handle)
            layer = LineSymbolLayer.create(handle)
            if layer:
                layer.read(handle)
            self.levels.extend([layer])

        # the next section varies in size. To handle this we jump forward to a known anchor
        # point, and then move back by a known amount

        # burn up to the 02
        while not binascii.hexlify(handle.file_handle.read(1)) == b'02':
            pass

        # jump back a known amount
        handle.file_handle.seek(handle.file_handle.tell() - 8 * number_layers - 1)

        for l in self.levels:
            l.read_enabled(handle)
        for l in self.levels:
            l.read_locked(handle)

        while not binascii.hexlify(handle.file_handle.read(1)) == b'02':
            pass

    @staticmethod
    def read_line_type(file_handle):
        """
        Interprets the line type bytes
        """
        line_type = unpack("<I", file_handle.read(4))[0]
        types = {0: 'solid',
                 1: 'dashed',
                 2: 'dotted',
                 3: 'dash dot',
                 4: 'dash dot dot',
                 5: 'null'
                 }
        if line_type not in types:
            raise UnreadableSymbolException('unknown line type {} at {}'.format(line_type, hex(file_handle.tell() - 4)))
        return types[line_type]


class FillSymbol(Symbol):
    """
    Fill symbol
    """

    def __init__(self):
        Symbol.__init__(self)

    def padding(self):
        return 10

    def _read(self, handle):
        self.color_model, self.color = read_color_and_model(handle.file_handle, debug=handle.debug)

        # useful stuff
        number_layers = unpack("<L", handle.file_handle.read(4))[0]
        if handle.debug:
            print('detected {} layers at {}'.format(number_layers, hex(handle.file_handle.tell() - 4)))

        for i in range(number_layers):
            consume_padding(handle.file_handle)
            layer = FillSymbolLayer.create(handle)
            if layer:
                layer.read(handle)
            self.levels.extend([layer])

        # the next section varies in size. To handle this we jump forward to a known anchor
        # point, and then move back by a known amount

        # burn up to the 02
        while not binascii.hexlify(handle.file_handle.read(1)) == b'02':
            pass

        # jump back a known amount
        handle.file_handle.seek(handle.file_handle.tell() - 8 * number_layers - 1)

        for l in self.levels:
            l.read_enabled(handle)
        for l in self.levels:
            l.read_locked(handle)


class MarkerSymbol(Symbol):
    """
    Marker symbol.

    """

    def __init__(self):
        Symbol.__init__(self)
        self.halo = False
        self.halo_size = 0
        self.halo_symbol = None

    def padding(self):
        return 10

    def _read(self, handle):
        # consume section of unknown purpose
        while not binascii.hexlify(handle.file_handle.read(1)) == b'40':
            pass
        consume_padding(handle.file_handle)

        self.color_model, self.color = read_color_and_model(handle.file_handle)

        self.halo = unpack("<L", handle.file_handle.read(4))[0] == 1
        self.halo_size = unpack("<d", handle.file_handle.read(8))[0]

        self.halo_symbol = create_object(handle)()
        self.halo_symbol.read(handle)

        # not sure about this - there's an extra 02 here if a full fill symbol is used for the halo
        if isinstance(self.halo_symbol, Symbol):
            while not binascii.hexlify(handle.file_handle.read(1)) == b'02':
                pass

        consume_padding(handle.file_handle)

        # useful stuff
        number_layers = unpack("<L", handle.file_handle.read(4))[0]

        if handle.debug:
            print('found {} layers at {}'.format(number_layers, hex(handle.file_handle.tell() - 4)))

        for i in range(number_layers):
            # consume_padding(handle.file_handle)
            layer = MarkerSymbolLayer.create(handle)
            if handle.debug:
                print('marker symbol layer at {}'.format(hex(handle.file_handle.tell())))

            layer.read(handle)
            self.levels.extend([layer])

        for l in self.levels:
            l.read_enabled(handle)
        for l in self.levels:
            l.read_locked(handle)


def read_symbol(file_handle, debug=False):
    """
    Reads a symbol from the specified file
    """
    handle = Handle(file_handle, debug)
    symbol_object = create_object(handle)

    try:

        # sometimes symbols are just layers, sometimes whole symbols...
        if issubclass(symbol_object, SymbolLayer):
            symbol_layer = symbol_object()
            symbol_layer.read(handle)
            return symbol_layer
        else:
            if not issubclass(symbol_object, Symbol):
                raise UnreadableSymbolException('Expected Symbol, got {}'.format(symbol_object))
            symbol = symbol_object()
            symbol.read(handle)
            return symbol

    except InvalidColorException:
        raise UnreadableSymbolException()
