#!/usr/bin/env python
"""
Binary stream representing persistent objects
"""

from struct import unpack, error
import binascii
from datetime import datetime, timedelta
import os
from typing import Optional
from slyr_community.parser.object_registry import ObjectRegistry, REGISTRY
from slyr_community.parser.object import Object
from slyr_community.parser.exceptions import UnsupportedVersionException, UnreadableSymbolException, \
    CustomExtensionClsidException


class Stream:
    """
    An input stream for object parsing
    """

    VBEMPTY = 0
    VBNULL = 1
    VBINTEGER = 2
    VBLONG = 3
    VBSINGLE = 4
    VBDOUBLE = 5
    VBCURRENCY = 6
    VBDATE = 7
    VBSTRING = 8
    VBOBJECT = 9
    VBERROR = 10
    VBBOOLEAN = 11
    VBVARIANT = 12
    VBDATAOBJECT = 13
    VBDECIMAL = 14
    VBBYTE = 17
    VBLONGLONG = 20
    VBUSERDEFINEDTYPE = 36
    VBARRAY = 8192
    USER_PASSWORD = 8209  # byte array

    def __init__(self, io_stream, debug: bool = False, offset: int = 0, force_layer=False, extract_doc_structure=True,
                 parse_doc_structure_only=False, tolerant=True, path=''):
        """
        Constructor for Streams
        :param io_stream: input stream, usually a file handle
        :param debug: true if debugging output should be created during object read
        :param offset: offset to start reading at
        """
        self._io_stream = io_stream
        self.debug = debug
        self.debug_depth = 0
        self.allow_shortcuts = True
        self.tolerant = tolerant

        current = io_stream.tell()
        io_stream.seek(0, os.SEEK_END)
        self.end = io_stream.tell()
        io_stream.seek(current)

        if offset > 0:
            self._io_stream.seek(offset)

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

    def read_uchar(self, debug_string: str = '', expected=None) -> int:
        """
        Reads a uchar from the stream.
        :return:
        """
        res = unpack("<B", self._io_stream.read(1))[0]
        if debug_string:
            self.log('read uchar {} of {}'.format(debug_string, res), 1)

        if not self.tolerant and expected is not None:
            try:
                assert res in expected, 'Got {}, expected {}'.format(res, expected)
            except TypeError:
                assert res == expected, 'Got {}, expected {}'.format(res, expected)

        return res

    def read_double(self, debug_string: str = '', expected=None) -> float:
        """
        Reads a double from the stream.
        :return:
        """
        res = unpack("<d", self._io_stream.read(8))[0]
        if debug_string:
            self.log('read double {} of {}'.format(debug_string, res), 8)

        if not self.tolerant and expected is not None:
            try:
                assert res in expected, 'Got {}, expected {}'.format(res, expected)
            except TypeError:
                assert res == expected, 'Got {}, expected {}'.format(res, expected)

        return res

    def read_int(self, debug_string: str = '', expected=None) -> int:
        """
        Reads an int from the stream.
        :return:
        """
        try:
            res = unpack("<L", self._io_stream.read(4))[0]
        except error:  # struct.error
            raise UnreadableSymbolException('Truncated integer')

        if debug_string:
            self.log('read int {} of {}'.format(debug_string, res), 4)

        if not self.tolerant and expected is not None:
            try:
                assert res in expected, 'Got {}, expected {}'.format(res, expected)
            except TypeError:
                assert res == expected, 'Got {}, expected {}'.format(res, expected)

        return res

    def read_uint(self, debug_string: str = '', expected=None) -> int:
        """
        Reads an uint from the stream.
        :return:
        """
        res = unpack("<I", self._io_stream.read(4))[0]
        if debug_string:
            self.log('read uint {} of {}'.format(debug_string, res), 4)

        if not self.tolerant and expected is not None:
            try:
                assert res in expected, 'Got {}, expected {}'.format(res, expected)
            except TypeError:
                assert res == expected, 'Got {}, expected {}'.format(res, expected)

        return res

    def read_signed_int(self, debug_string: str = '', expected=None) -> int:
        """
        Reads a signed int from the stream.
        :return:
        """
        res = unpack("<i", self._io_stream.read(4))[0]
        if debug_string:
            self.log('read signed int {} of {}'.format(debug_string, res), 4)

        if not self.tolerant and expected is not None:
            try:
                assert res in expected, 'Got {}, expected {}'.format(res, expected)
            except TypeError:
                assert res == expected, 'Got {}, expected {}'.format(res, expected)

        return res

    def read_ulong(self, debug_string: str = '', expected=None) -> int:
        """
        Reads an ulong from the stream.
        :return:
        """
        res = unpack("<l", self._io_stream.read(4))[0]
        if debug_string:
            self.log('read ulong {} of {}'.format(debug_string, res), 4)

        if not self.tolerant and expected is not None:
            try:
                assert res in expected, 'Got {}, expected {}'.format(res, expected)
            except TypeError:
                assert res == expected, 'Got {}, expected {}'.format(res, expected)

        return res

    def read_ushort(self, debug_string: str = '', expected=None) -> int:
        """
        Reads an unsigned short from the stream.
        :return:
        """
        res = unpack("<H", self._io_stream.read(2))[0]
        if debug_string:
            self.log('read ushort {} of {}'.format(debug_string, res), 2)

        if not self.tolerant and expected is not None:
            try:
                assert res in expected, 'Got {}, expected {}'.format(res, expected)
            except TypeError:
                assert res == expected, 'Got {}, expected {}'.format(res, expected)

        return res

    def read_clsid(self, debug_string: str = '') -> str:
        """
        Reads a CLSID from the stream
        """
        clsid_bin = binascii.hexlify(self._io_stream.read(16))

        clsid = ObjectRegistry.hex_to_clsid2(clsid_bin)
        if debug_string and clsid != '00000000-0000-0000-0000-000000000000':
            self.log('Found {} clsid of {}'.format(debug_string, clsid), 16)
        return clsid

    def read_raw_clsid(self, debug_string: str = '', expected=None) -> str:
        """
        Reads a CLSID from the stream
        """
        clsid_bin = binascii.hexlify(self._io_stream.read(16))
        clsid = ObjectRegistry.hex_to_clsid(clsid_bin)
        if debug_string and clsid != '00000000-0000-0000-0000-000000000000':
            self.log('Found {} clsid of {}'.format(debug_string, clsid), 16)

        if not self.tolerant and expected is not None:
            if isinstance(expected, (tuple, list)):
                assert clsid in expected, 'Got {}, expected {}'.format(clsid, expected)
            else:
                assert clsid == expected, 'Got {}, expected {}'.format(clsid, expected)

        return clsid

    def read_string(self, debug_string: str = '', expected=None, size=None) -> str:
        """
        Decodes a string from the binary

        From the .dot BinaryWriter code: 'This method first writes the length of the string as
        a four-byte unsigned integer, and then writes that many characters
        to the stream'
        """
        if debug_string:
            self.log('start {}'.format(debug_string))

        length = size if size is not None else self.read_uint('{} string length'.format(debug_string))
        if length < 2:
            raise UnreadableSymbolException('Invalid length of string {}'.format(length))

        self.log('string of length {}'.format(int(length / 2 - 1)), 4)
        buffer = self._io_stream.read(length - 2)
        string = buffer.decode('utf-16')
        terminator = binascii.hexlify(self._io_stream.read(2))
        if not terminator == b'0000':
            raise UnreadableSymbolException('Invalid string terminator')

        self.log('found string "{}"'.format(string))

        if not self.tolerant and expected is not None:
            if isinstance(expected, (tuple, list)):
                assert string in expected, 'Got {}, expected {}'.format(string, expected)
            else:
                assert string == expected, 'Got {}, expected {}'.format(string, expected)

        return string

    def read_stringv2(self, debug_string: str = '', expected=None) -> str:
        """
        Decodes a string from the binary, alternative method
        """
        if debug_string:
            self.log('start {}'.format(debug_string))

        length = self.read_uint('{} string length'.format(debug_string))
        if length < 0:
            raise UnreadableSymbolException('Invalid length of string {}'.format(length))

        self.log('string of length {}'.format(length), 4)
        if length != 0:
            buffer = self._io_stream.read(length * 2)
            string = buffer.decode('utf-16')
            terminator = binascii.hexlify(self._io_stream.read(2))

            self.log('found string "{}"'.format(string))
            if not terminator == b'0000':
                raise UnreadableSymbolException('Invalid string terminator')
        else:
            string = ''

        if not self.tolerant and expected is not None:
            if isinstance(expected, (tuple, list)):
                assert string in expected, 'Got "{}", expected {}'.format(string, expected)
            else:
                assert string == expected, 'Got "{}", expected {}'.format(string, expected)

        return string

    def read_string_terminated(self, debug_string: str = '', expected=None) -> str:
        """
        Decodes a string from the binary, with no length but scanning for terminators
        """
        if debug_string:
            self.log('start {}'.format(debug_string))

        string = ''
        res = self.read(2)
        while res != b'\x00\x00':
            string += res.decode('utf-16')
            res = self.read(2)

        self.log('found string "{}"'.format(string))

        if not self.tolerant and expected is not None:
            if isinstance(expected, (tuple, list)):
                assert string in expected, 'Got "{}", expected {}'.format(string, expected)
            else:
                assert string == expected, 'Got "{}", expected {}'.format(string, expected)

        return string

    def read_ascii(self, debug_string: str = '', expected=None, length=None) -> str:
        """
        Decodes an ascii string from the binary
        """
        if debug_string:
            self.log('start {}'.format(debug_string))

        length = length if length is not None else unpack("<L", self._io_stream.read(4))[0]
        self.log('string of length {}'.format(int(length)), 4)
        if length == 0:
            return ''

        self.log('ascii of length {}'.format(length))
        # encoding?
        b = self.read(length)
        res = b.decode('latin-1')
        self.log('found ascii "{}"'.format(res))

        if not self.tolerant and expected is not None:
            if isinstance(expected, (tuple, list)):
                assert res in expected, 'Got "{}", expected "{}"'.format(res, expected)
            else:
                assert res == expected, 'Got "{}", expected "{}"'.format(res, expected)

        return res

    def read_object(self, debug_string: str = '', _=True, __=False) -> Optional[Object]:
        """
        Creates and reads a new object from the stream
        """
        clsid = self.read_clsid(debug_string)
        try:
            res = REGISTRY.create_object(clsid)
        except CustomExtensionClsidException as e:
            self.debug_depth += 1
            self.log('!!!Custom extension encountered -- cannot read ({})'.format(e), 16)
            self.debug_depth -= 1
            raise e

        if res is not None:
            self.log('** {} **'.format(res.__class__.__name__), 16)
        else:
            self.log('{} not found'.format(debug_string), 16)

        if res is not None:
            self.debug_depth += 1

            version = 1
            compatible_versions = res.compatible_versions()
            if compatible_versions is not None:
                version = self.read_ushort('version')
                if version not in res.compatible_versions():
                    supported_versions = ','.join([str(v) for v in res.compatible_versions()])
                    raise UnsupportedVersionException(
                        'Cannot read {} version {}, only support version(s): {}'.format(
                            res.__class__.__name__, version, supported_versions))

            res.version = version
            try:
                res.read(self, version)
            except CustomExtensionClsidException as e:
                self.log('!!!Custom extension encountered -- only partial read of {}'.format(res.__class__.__name__),
                         16)
                e.object = res
                self.debug_depth -= 1
                raise e
            self.log('ended {}'.format(res.__class__.__name__))

            if self.debug:
                print('')
            self.debug_depth -= 1

        return res

    def read_picture(self, debug_string: str = ''):
        """
        Reads an embedded picture from the stream and returns it
        """
        from slyr_community.parser.objects.picture import Picture

        self.log('Reading picture {}'.format(debug_string))
        pic = Picture.create_from_stream(self)
        return pic

    def read_variant(self, variant_type=None, debug_string: str = '', expected=None):
        if debug_string:
            self.log('reading variant {}'.format(debug_string))
        if variant_type is None:
            variant_type = self.read_ushort('type')
        if variant_type == Stream.VBSTRING:
            value = self.read_string('value')
        elif variant_type == Stream.VBLONG:
            value = self.read_ulong('value')
        elif variant_type == Stream.VBSINGLE:
            value = self.read_int('value')
        elif variant_type == Stream.VBINTEGER:
            value = self.read_ushort('value')
        elif variant_type in (Stream.VBNULL, Stream.VBEMPTY):
            value = None
        elif variant_type == Stream.VBDOUBLE:
            value = self.read_double('value')
        elif variant_type == Stream.VBBOOLEAN:
            value = self.read_ushort('value') != 0
        elif variant_type == Stream.VBDATE:
            value = datetime.strftime(
                datetime(year=100, month=1, day=1) + timedelta(days=self.read_double('value') + 657434),
                '%Y-%m-%d %H:%M:%S')
        elif variant_type == Stream.USER_PASSWORD:
            length = self.read_uint('password length')
            value = '*' * length
            self.read(length)
        elif variant_type == Stream.VBDATAOBJECT:
            value = self.read_object('value')
        else:
            raise UnreadableSymbolException('Unknown property type {}'.format(variant_type))

        if not self.tolerant and expected is not None:
            if isinstance(expected, (tuple, list)):
                assert value in expected, 'Got {}, expected {}'.format(value, expected)
            else:
                assert value == expected, 'Got {}, expected {}'.format(value, expected)

        return value
