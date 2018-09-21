#!/usr/bin/env python

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

    def log(self, message: str, offset: int = 0 ):
        """
        Logs a debug message
        """
        if self.debug:
            print('{} at {}'.format(message, hex(self._io_stream.tell()-offset)))

    def read_double(self, debug_string: str = '') -> float:
        """
        Reads a double from the stream.
        :return:
        """
        res = unpack("<d", self._io_stream.read(8))[0]
        if debug_string and self.debug:
            print('read {} of {} at {}'.format(debug_string, res, hex(self._io_stream.tell() - 8)))
        return res

    def read_int(self, debug_string: str = '') -> int:
        """
        Reads an int from the stream.
        :return:
        """
        res = unpack("<L", self._io_stream.read(4))[0]
        if debug_string and self.debug:
            print('read {} of {} at {}'.format(debug_string, res, hex(self._io_stream.tell() - 4)))
        return res

    def read_uint(self, debug_string: str = '') -> int:
        """
        Reads an uint from the stream.
        :return:
        """
        res = unpack("<I", self._io_stream.read(4))[0]
        if debug_string and self.debug:
            print('read {} of {} at {}'.format(debug_string, res, hex(self._io_stream.tell() - 4)))
        return res

    def read_guid(self) -> str:
        """
        Reads a GUID from the stream
        """
        if self.debug:
            print('Reading object header at {}'.format(hex(self._io_stream.tell())))
        guid_bin = binascii.hexlify(self._io_stream.read(16))

        guid = ObjectRegistry.hex_to_guid(guid_bin)
        if self.debug:
            print('Found guid of {}'.format(guid))
        return guid

    def read_string(self, debug_string: str = '') -> str:
        """
        Decodes a string from the binary

        From the .dot BinaryWriter code: 'This method first writes the length of the string as
        a four-byte unsigned integer, and then writes that many characters
        to the stream'
        """
        start = self._io_stream.tell()
        if debug_string and self.debug:
            print('start {} at {}'.format(debug_string, hex(start)))

        length = unpack("<I", self._io_stream.read(4))[0]
        if self.debug:
            print('string of length {} at {}'.format(length, hex(start)))
        buffer = self._io_stream.read(length)
        string = buffer.decode('utf-16')
        if self.debug:
            print('found string "{}" at {}'.format(string, hex(start)))
        return string[:-1]

    def read_object(self) -> Optional[Object]:
        """
        Creates and reads a new object from the stream
        """
        guid = self.read_guid()
        res = REGISTRY.create_object(guid)
        if self.debug:
            if res is not None:
                print('=={}'.format(res.__class__.__name__))
            else:
                print('==None')

        if res is not None:
            res.read(self)
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
