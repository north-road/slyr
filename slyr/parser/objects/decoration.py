from slyr.parser.object import Object
from slyr.parser.stream import Stream


class LineDecoration(Object):

    def __init__(self):
        super().__init__()
        self.decorations = []

    @staticmethod
    def guid():
        return '533d88f5-0a1a-11d2-b27f-0000f878229e'

    def read(self, stream: Stream):
        """
        Reads the decoration information
        """
        stream.read(2)  # unknown -- maybe includes position as ratio?

        # next bit is probably number of decorations?
        count = stream.read_uint('count of decorations')
        for i in range(count):
            decoration = stream.read_object('decoration element')
            self.decorations.append(decoration)


class SimpleLineDecoration(Object):
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

    @staticmethod
    def guid():
        return '533d88f3-0a1a-11d2-b27f-0000f878229e'

    def read(self, stream: Stream):
        """
        Reads the decoration information
        """
        stream.read(2)  # unknown -- maybe includes position as ratio?

        self.fixed_angle = not bool(stream.read_uchar())
        stream.log('detected {}'.format('fixed angle' if self.fixed_angle else 'not fixed angle'))
        self.flip_first = bool(stream.read_uchar())
        stream.log('detected {}'.format('flip first' if self.flip_first else 'no flip first'))
        self.flip_all = bool(stream.read_uchar())
        stream.log('detected {}'.format('flip all' if self.flip_all else 'no flip all'))

        stream.read(2)  # unknown -- maybe includes position as ratio?

        self.marker = stream.read_object('marker')

        # if False and not issubclass(self.marker.__class__, SymbolLayer):
        #    # TODO ewwwwww
        #    while not binascii.hexlify(handle._io_stream.read(1)) == b'02':
        #        pass
        #    while not binascii.hexlify(handle._io_stream.read(1)) == b'02':
        #        pass
        #    handle._io_stream.read(5)

        # next bit is the number of doubles coming next
        marker_number_positions = stream.read_uint('marker positions')

        # next bit is the positions themselves -- maybe we can infer this from the number of positions
        # alone. E.g. 2 positions = 0, 1. 3 positions = 0, 0.5, 1
        for i in range(marker_number_positions):
            self.marker_positions.append(stream.read_double())
        stream.log('marker positions are {}'.format(self.marker_positions))
