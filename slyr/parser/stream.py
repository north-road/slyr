#!/usr/bin/env python
"""
Binary stream representing persistent objects
"""

from struct import unpack
import binascii
from typing import Optional
from slyr.parser.object_registry import ObjectRegistry, REGISTRY
from slyr.parser.object import Object


class Stream:
    """
    An input stream for object parsing
    """

    def __init__(self, io_stream, debug: bool = False):
        """
        Constructor for Streams
        :param io_stream: input stream, usually a file handle
        :param debug: true if debugging output should be created during object read
        """
        self._io_stream = io_stream
        self.debug = debug
        self.debug_depth = 0

    def tell(self) -> int:
        """
        Returns the current position within the stream.
        """
        return self._io_stream.tell()

    def read(self, length: int) -> bin:
        """
        Reads the from the stream for the given length and returns
        the binary result.
        """
        return self._io_stream.read(length)

    def seek(self, offset: int):
        """
        Seeks for the given offset.
        """
        self._io_stream.seek(offset)

    def rewind(self, length):
        """
        Rewinds by the given length
        """
        self._io_stream.seek(self._io_stream.tell() - length)

    def log(self, message: str, offset: int = 0):
        """
        Logs a debug message
        """
        if self.debug:
            print('{}{} at {}'.format('   ' * self.debug_depth, message, hex(self._io_stream.tell() - offset)))

    def read_uchar(self, debug_string: str = '') -> int:
        """
        Reads a uchar from the stream.
        :return:
        """
        res = unpack("<B", self._io_stream.read(1))[0]
        if debug_string:
            self.log('read uchar {} of {}'.format(debug_string, res), 1)
        return res

    def read_double(self, debug_string: str = '') -> float:
        """
        Reads a double from the stream.
        :return:
        """
        res = unpack("<d", self._io_stream.read(8))[0]
        if debug_string:
            self.log('read double {} of {}'.format(debug_string, res), 8)
        return res

    def read_int(self, debug_string: str = '') -> int:
        """
        Reads an int from the stream.
        :return:
        """
        res = unpack("<L", self._io_stream.read(4))[0]
        if debug_string:
            self.log('read int {} of {}'.format(debug_string, res), 4)
        return res

    def read_uint(self, debug_string: str = '') -> int:
        """
        Reads an uint from the stream.
        :return:
        """
        res = unpack("<I", self._io_stream.read(4))[0]
        if debug_string:
            self.log('read uint {} of {}'.format(debug_string, res), 4)
        return res

    def read_guid(self, debug_string: str = '') -> str:
        """
        Reads a GUID from the stream
        """
        guid_bin = binascii.hexlify(self._io_stream.read(16))

        guid = ObjectRegistry.hex_to_guid(guid_bin)
        if guid != '00000000-0000-0000-0000-000000000000':
            self.log('Found {} guid of {}'.format(debug_string, guid), 16)
        return guid

    def read_string(self, debug_string: str = '') -> str:
        """
        Decodes a string from the binary

        From the .dot BinaryWriter code: 'This method first writes the length of the string as
        a four-byte unsigned integer, and then writes that many characters
        to the stream'
        """
        if debug_string:
            self.log('start {}'.format(debug_string))

        length = unpack("<I", self._io_stream.read(4))[0]
        self.log('string of length {}'.format(length), 4)
        buffer = self._io_stream.read(length)
        string = buffer.decode('utf-16')
        self.log('found string "{}"'.format(string))
        return string[:-1]

    def read_object(self, debug_string: str = '') -> Optional[Object]:
        """
        Creates and reads a new object from the stream
        """
        guid = self.read_guid(debug_string)
        res = REGISTRY.create_object(guid)
        if res is not None:
            self.log('** {} **'.format(res.__class__.__name__), 16)
        else:
            self.log('{} not found'.format(debug_string), 16)

        if res is not None:
            self.debug_depth += 1
            res.read(self)
            self.log('ended {}'.format(res.__class__.__name__))
            if self.debug:
                print('')
            self.debug_depth -= 1

        return res

    def consume_padding(self):
        """
        Swallows up '00' padding from a file handle.

        Use with caution! This is fragile if a possible valid '00' byte follows the padding.
        """
        last_position = self._io_stream.tell()
        while binascii.hexlify(self._io_stream.read(1)) == b'00':
            last_position = self._io_stream.tell()
        self._io_stream.seek(last_position)
