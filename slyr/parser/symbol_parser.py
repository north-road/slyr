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


def guid_to_hex(guid: str):
    # I don't understand the reason why, but GUIDs are stored in a strange format
    # in the blobs. E.g. a GUID of
    # 7914e603-c892-11d0-8bb6-080009ee4e41
    # is stored as
    # 03e6147992c8d0118bb6080009ee4e41
    # This function converts GUIDs to the blob format

    guid = guid.replace('-', '')
    bytes = b''
    bytes += guid[6:8].encode()
    bytes += guid[4:6].encode()
    bytes += guid[2:4].encode()
    bytes += guid[0:2].encode()
    bytes += guid[10:12].encode()
    bytes += guid[8:10].encode()
    bytes += guid[14:16].encode()
    bytes += guid[12:14].encode()
    bytes += guid[16:].encode()
    return bytes


def hex_to_guid(hex_value) -> str:
    """
    Converts a binary value to a GUID
    eg 03e6147992c8d0118bb6080009ee4e41
    to 7914e603-c892-11d0-8bb6-080009ee4e41
    """
    res = ''
    res += hex_value[6:8].decode()
    res += hex_value[4:6].decode()
    res += hex_value[2:4].decode()
    res += hex_value[0:2].decode()
    res += '-'
    res += hex_value[10:12].decode()
    res += hex_value[8:10].decode()
    res += '-'
    res += hex_value[14:16].decode()
    res += hex_value[12:14].decode()
    res += '-'
    res += hex_value[16:20].decode()
    res += '-'
    res += hex_value[20:].decode()
    return res


def guid_to_object(guid):
    GUIDS = {
        '88539431-e06e-11d1-b277-0000f878229e': ArrowMarkerSymbolLayer,
        '7914e5fb-c892-11d0-8bb6-080009ee4e41': CartographicLineSymbolLayer,
        '7914e600-c892-11d0-8bb6-080009ee4e41': CharacterMarkerSymbolLayer,
        # DotDensityFillSymbol: 9a1eba10-cdf9-11d3-81eb-0080c79f0371
        # GradientFillSymbol: 7914e609-c892-11d0-8bb6-080009ee4e41
        # HashLineSymbol: 7914e5fc-c892-11d0-8bb6-080009ee4e41
        # LineFillSymbol: 7914e606-c892-11d0-8bb6-080009ee4e41
        # MarkerFillSymbol: 7914e608-c892-11d0-8bb6-080009ee4e41
        '7914e5fd-c892-11d0-8bb6-080009ee4e41': MarkerLineSymbolLayer,
        '7914e604-c892-11d0-8bb6-080009ee4e41': FillSymbol,
        '7914e5fa-c892-11d0-8bb6-080009ee4e41': LineSymbol,
        '7914e5ff-c892-11d0-8bb6-080009ee4e41': MarkerSymbol,
        # PictureFillSymbol: d842b082-330c-11d2-9168-0000f87808ee
        # PictureLineSymbol: 22c8c5a1-84fc-11d4-834d-0080c79f0371
        # PictureMarkerSymbol: 7914e602-c892-11d0-8bb6-080009ee4e41
        '7914e603-c892-11d0-8bb6-080009ee4e41': SimpleFillSymbolLayer,
        '7914e5f9-c892-11d0-8bb6-080009ee4e41': SimpleLineSymbolLayer,
        '7914e5fe-c892-11d0-8bb6-080009ee4e41': SimpleMarkerSymbolLayer,
        '533d88f5-0a1a-11d2-b27f-0000f878229e': LineDecoration,
        '533d88f3-0a1a-11d2-b27f-0000f878229e': SimpleLineDecoration,
        '539431ff-6e88-d1e0-11b2-770000f87822': SimpleLineDecoration, #### TODO - not correct???
        # TextSymbol: b65a3e74-2993-11d1-9a43-0080c7ec5c96
        # RgbColor: 7ee9c496-d123-11d0-8383-080009b996cc
        # CmykColor: 7ee9c497-d123-11d0-8383-080009b996cc
        # GrayColor: 7ee9c495-d123-11d0-8383-080009b996cc
        # HlsColor: 7ee9c493-d123-11d0-8383-080009b996cc
        # HsvColor: 7ee9c492-d123-11d0-8383-080009b996cc
        # Font: 0be35203-8f91-11ce-9de3-00aa004bb851
    }

    NOT_IMPLEMENTED_GUIDS = {
        '9a1eba10-cdf9-11d3-81eb-0080c79f0371': 'DotDensityFillSymbol',
        '7914e609-c892-11d0-8bb6-080009ee4e41': 'GradientFillSymbol',
        '7914e5fc-c892-11d0-8bb6-080009ee4e41': 'HashLineSymbol',
        '7914e606-c892-11d0-8bb6-080009ee4e41': 'LineFillSymbol',
        '7914e608-c892-11d0-8bb6-080009ee4e41': 'MarkerFillSymbol',
        'd842b082-330c-11d2-9168-0000f87808ee': 'PictureFillSymbol',
        '22c8c5a1-84fc-11d4-834d-0080c79f0371': 'PictureLineSymbol',
        '7914e602-c892-11d0-8bb6-080009ee4e41': 'PictureMarkerSymbol',
        'b65a3e74-2993-11d1-9a43-0080c7ec5c96': 'TextSymbol',
        '7ee9c496-d123-11d0-8383-080009b996cc': 'RgbColor',
        '7ee9c497-d123-11d0-8383-080009b996cc': 'CmykColor',
        '7ee9c495-d123-11d0-8383-080009b996cc': 'GrayColor',
        '7ee9c493-d123-11d0-8383-080009b996cc': 'HlsColor',
        '7ee9c492-d123-11d0-8383-080009b996cc': 'HsvColor',
        '0be35203-8f91-11ce-9de3-00aa004bb851': 'Font'
    }

    if guid in NOT_IMPLEMENTED_GUIDS:
        raise UnreadableSymbolException('{} are not implemented yet'.format(NOT_IMPLEMENTED_GUIDS[guid]))

    if guid not in GUIDS:
        raise UnreadableSymbolException('Unknown GUID {}'.format(guid))

    return GUIDS[guid]


def create_object(handle):
    """
    Reads an object header and returns the corresponding object class
    """
    if handle.debug:
        print('Reading object header at {}'.format(hex(handle.file_handle.tell())))
    guid_bin = binascii.hexlify(handle.file_handle.read(16))
    guid = hex_to_guid(guid_bin)
    if handle.debug:
        print('Found guid of {}'.format(guid))

    object_type = guid_to_object(guid)
    return object_type


class LineDecoration:
    pass


class SimpleLineDecoration:
    pass

def read_magic_3(handle):
    """
    Consumes an expected magic sequence (3), of unknown purpose
    """
    magic_3 = binascii.hexlify(handle.file_handle.read(16))
    if magic_3 != b'883d531a0ad211b27f0000f878229e01':
        raise UnreadableSymbolException(
            'Differing magic string 3: {} at {}'.format(magic_3, hex(handle.file_handle.tell() - 16)))

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

    @staticmethod
    def read_cap(file_handle):
        cap_bin = unpack("<B", file_handle.read(1))[0]
        if cap_bin == 0:
            return 'butt'
        elif cap_bin == 1:
            return 'round'
        elif cap_bin == 2:
            return 'square'
        else:
            raise UnreadableSymbolException('unknown cap style {}'.format(cap_bin))

    @staticmethod
    def read_join(file_handle):
        join_bin = unpack("<B", file_handle.read(1))[0]
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
        start_decoration = create_object(handle)

        handle.file_handle.read(1)

        unknown = unpack("<L", handle.file_handle.read(4))[0]
        if handle.debug:
            print('read unknown int of {} at {}'.format(unknown, hex(handle.file_handle.tell() - 4)))

        handle.file_handle.read(1)

        result = {}

        end_decoration = create_object(handle)
        handle.file_handle.read(1)
        result['marker_fixed_angle'] = not bool(unpack("<B", handle.file_handle.read(1))[0])
        if handle.debug:
            print('detected {} at {}'.format('fixed angle' if result['marker_fixed_angle'] else 'not fixed angle',
                                             hex(handle.file_handle.tell() - 1)))
        result['marker_flip_first'] = bool(unpack("<B", handle.file_handle.read(1))[0])
        if handle.debug:
            print('detected {} at {}'.format('flip first' if result['marker_flip_first'] else 'no flip first',
                                             hex(handle.file_handle.tell() - 1)))
        result['marker_flip_all'] = bool(unpack("<B", handle.file_handle.read(1))[0])
        if handle.debug:
            print('detected {} at {}'.format('flip all' if result['marker_flip_all'] else 'no flip all',
                                             hex(handle.file_handle.tell() - 1)))

        handle.file_handle.read(2)
        result['marker'] = create_object(handle)()
        result['marker'].read(handle)

        if not issubclass(result['marker'].__class__, SymbolLayer):
            # TODO ewwwwww
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
        result['marker_positions'] = []
        for i in range(marker_number_positions):
            result['marker_positions'].append(unpack("<d", handle.file_handle.read(8))[0])
        if handle.debug:
            print('marker positions are {}'.format(result['marker_positions']))
            print('ended carto marker at {}'.format(hex(handle.file_handle.tell() - 1)))

        return result


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

    def _read(self, handle):
        self.cap = self.read_cap(handle.file_handle)

        unknown = binascii.hexlify(handle.file_handle.read(3))
        if unknown != b'000000':
            raise UnreadableSymbolException('Differing unknown string {}'.format(unknown))
        self.join = self.read_join(handle.file_handle)
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
            handle.file_handle.seek(handle.file_handle.tell() - 1)
            end_markers = self.read_end_markers(handle)
            self.marker_fixed_angle = end_markers['marker_fixed_angle']
            self.marker_flip_first = end_markers['marker_flip_first']
            self.marker_flip_all = end_markers['marker_flip_all']
            self.marker = end_markers['marker']
            self.marker_positions = end_markers['marker_positions']


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
        self.cap = self.read_cap(handle.file_handle)
        if handle.debug:
            print('read cap of {} at {}'.format(self.cap, hex(handle.file_handle.tell() - 1)))

        self.offset = unpack("<d", handle.file_handle.read(8))[0]
        if handle.debug:
            print('read offset of {} at {}'.format(self.offset, hex(handle.file_handle.tell() - 8)))

        self.pattern_marker = create_object(handle)()
        self.pattern_marker.read(handle)
        if handle.debug:
            print('back at marker line at {}'.format(hex(handle.file_handle.tell())))

        if not issubclass(self.pattern_marker.__class__, SymbolLayer):
            # ewwwwww
            while not binascii.hexlify(handle.file_handle.read(1)) == b'02':
                pass
            while not binascii.hexlify(handle.file_handle.read(1)) == b'02':
                pass
            handle.file_handle.read(5)

        handle.file_handle.read(18)
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
            print('deciphered marker line pattern ending at {}'.format(hex(handle.file_handle.tell())))
            pattern = ''
            for p in self.pattern_parts:
                pattern += '-' * int(p[0]) + '.' * int(p[1])
            print(pattern)

        if binascii.hexlify(handle.file_handle.read(1)) == b'f5':
            if handle.debug:
                print('detected end markers at {}'.format(hex(handle.file_handle.tell() - 1)))
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
