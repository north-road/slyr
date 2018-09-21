from slyr.parser.object import Object
from slyr.parser.stream import Stream
from slyr.parser.object_registry import REGISTRY
from struct import unpack


class Font(Object):

    def __init__(self):
        super().__init__()
        self.font = ''

    @staticmethod
    def guid():
        return '0be35203-8f91-11ce-9de3-00aa004bb851'

    def read(self, stream: Stream):
        stream.read(9)
        skip = unpack(">H", stream.read(2))[0]
        stream.log('font name for {}'.format(skip))
        stream.read(skip)


REGISTRY.register_object(Font)