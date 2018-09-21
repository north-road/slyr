
import binascii
from slyr.parser.object import Object
from slyr.parser.stream import Stream

class SymbolLayer(Object):
    """
    Base class for symbol layers
    """

    def __init__(self):
        self.locked = False
        self.enabled = True

    def padding(self):
        return 2

    def read_enabled(self, stream: Stream):
        """
        Reads the layer 'enabled' state
        """
        enabled = stream.read_uint()
        self.enabled = enabled == 1
        stream.log('read enabled ({})'.format(self.enabled), 4)

    def read_locked(self, stream: Stream):
        """
        Reads the layer 'locked' state

        """
        locked = stream.read_uint()
        self.locked = locked == 1
        stream.log('read layer locked ({})'.format(self.locked), 4)

    def _read(self, stream: Stream):
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

    def read(self, stream: Stream):
        """
        Reads the symbol layer information. Internally calls _read method
        for individual layer types
        """
        stream.log('skipping padding of {}'.format(self.padding()))
        stream.read(self.padding())

        self._read(stream)

        # look for 0d terminator
        if self.terminator() is not None:
            stream.log('looking for {}'.format(self.terminator()))

            terminator_len = int(len(self.terminator()[0]) / 2)
            while True:
                start = stream.tell()
                if binascii.hexlify(stream.read(terminator_len)) in self.terminator():
                    break
                stream.seek(start + 1)

        stream.log('finished layer read')