import binascii
from slyr.parser.objects.symbol_layer import SymbolLayer
from slyr.parser.stream import Stream
from slyr.parser.exceptions import UnreadableSymbolException
from slyr.parser.object_registry import REGISTRY


class LineSymbolLayer(SymbolLayer):
    """
    Base class for line symbol layers
    """

    def __init__(self):
        super().__init__()
        self.color = None

    @staticmethod
    def read_cap(stream: Stream):
        cap_bin = stream.read_uchar()
        if cap_bin == 0:
            return 'butt'
        elif cap_bin == 1:
            return 'round'
        elif cap_bin == 2:
            return 'square'
        else:
            raise UnreadableSymbolException('unknown cap style {}'.format(cap_bin))

    @staticmethod
    def read_join(stream: Stream):
        join_bin = stream.read_uchar()
        if join_bin == 0:
            return 'miter'
        elif join_bin == 1:
            return 'round'
        elif join_bin == 2:
            return 'bevel'
        else:
            raise UnreadableSymbolException('unknown join style {}'.format(join_bin))

    @staticmethod
    def read_line_type(stream: Stream):
        """
        Interprets the line type bytes
        """
        line_type = stream.read_uint()
        types = {0: 'solid',
                 1: 'dashed',
                 2: 'dotted',
                 3: 'dash dot',
                 4: 'dash dot dot',
                 5: 'null'
                 }
        if line_type not in types:
            raise UnreadableSymbolException('unknown line type {} at {}'.format(line_type, hex(stream.tell() - 4)))
        return types[line_type]

    @staticmethod
    def read_end_markers(stream: Stream):
        line_decoration = stream.read_object()
        return line_decoration


class SimpleLineSymbolLayer(LineSymbolLayer):
    """
    Simple line symbol layer
    """

    def __init__(self):
        super().__init__()
        self.width = None
        self.line_type = None

    @staticmethod
    def guid():
        return '7914e5f9-c892-11d0-8bb6-080009ee4e41'

    def _read(self, stream: Stream):
        self.color = stream.read_object()
        self.width = stream.read_double('width')

        self.line_type = self.read_line_type(stream)
        stream.log('read line type of {}'.format(self.line_type))


class CartographicLineSymbolLayer(LineSymbolLayer):
    """
    Cartographic line symbol layer
    """

    def __init__(self):
        super().__init__()
        self.width = None
        self.cap = None
        self.join = None
        self.offset = None
        self.template = None
        self.decoration = None

    @staticmethod
    def guid():
        return '7914e5fb-c892-11d0-8bb6-080009ee4e41'

    def padding(self):
        return 2

    def _read(self, stream: Stream):
        self.cap = self.read_cap(stream)

        unknown = binascii.hexlify(stream.read(3))
        if unknown != b'000000':
            raise UnreadableSymbolException('Differing unknown string {}'.format(unknown))
        self.join = self.read_join(stream)
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

        self.decoration = stream.read_object()


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

    @staticmethod
    def guid():
        return '7914e5fd-c892-11d0-8bb6-080009ee4e41'

    def padding(self):
        return 2

    def _read(self, stream: Stream):
        self.cap = self.read_cap(stream)
        stream.log('read cap of {}'.format(self.cap), -1)

        self.offset = stream.read_double('offset')

        self.pattern_marker = stream.read_object()
        stream.log('back at marker line')

        #if False and not issubclass(self.pattern_marker.__class__, SymbolLayer):
        #    # ewwwwww
        #    while not binascii.hexlify(handle._io_stream.read(1)) == b'02':
        #        pass
        #    while not binascii.hexlify(handle._io_stream.read(1)) == b'02':
        #        pass
        #    handle._io_stream.read(5)

        stream.read(18)
        self.pattern_interval = stream.read_double('interval')

        # symbol pattern
        pattern_part_count = stream.read_int('pattern parts')

        self.pattern_parts = []
        for p in range(pattern_part_count):
            filled_squares = stream.read_double()
            empty_squares = stream.read_double()
            self.pattern_parts.append([filled_squares, empty_squares])

        pattern = ''
        for p in self.pattern_parts:
            pattern += '-' * int(p[0]) + '.' * int(p[1])
        stream.log('deciphered marker line pattern {}'.format(pattern))

        if binascii.hexlify(stream.read(1)) == b'f5':
            stream.log('detected end markers', -1)
            end_markers = self.read_end_markers(stream)
            self.marker_fixed_angle = end_markers['marker_fixed_angle']
            self.marker_flip_first = end_markers['marker_flip_first']
            self.marker_flip_all = end_markers['marker_flip_all']
            self.marker = end_markers['marker']
            self.marker_positions = end_markers['marker_positions']


REGISTRY.register(SimpleLineSymbolLayer)
REGISTRY.register(CartographicLineSymbolLayer)
REGISTRY.register(MarkerLineSymbolLayer)
