#!/usr/bin/env python
"""
Binary stream representing persistent objects
"""

# pylint: disable=too-many-lines

import binascii
import os
from datetime import datetime, timedelta
from io import BytesIO
from struct import unpack, error
from typing import Optional

from .exceptions import (
    UnsupportedVersionException,
    UnreadableSymbolException,
    EmptyDocumentException,
    DocumentTypeException,
    CustomExtensionClsidException,
    NotImplementedException,
    UnknownClsidException,
    PartiallyImplementedException
)
from .object import Object
from .object_registry import ObjectRegistry, REGISTRY


class Stream:  # pylint: disable=too-many-public-methods
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

    def __init__(self,  # pylint: disable=too-many-locals,too-many-branches,too-many-statements
                 io_stream,
                 debug: bool = False,
                 offset: int = 0,
                 force_layer=False,
                 extract_doc_structure=True,
                 parse_doc_structure_only=False,
                 tolerant=True,
                 path=''):
        """
        Constructor for Streams
        :param io_stream: input stream, usually a file handle
        :param debug: true if debugging output should be created during object read
        :param offset: offset to start reading at
        """
        self.io_stream = io_stream
        self.debug = debug
        self.is_layer = force_layer
        self.debug_depth = 0
        self.objects = [{}]
        self.unknown_objects = {}
        self.not_implemented_objects = {}
        self.current_ref_depth = -1
        self.tolerant = tolerant
        self.parse_doc_structure_only = parse_doc_structure_only
        self.allow_shortcuts = True

        # OLE document properties
        self.sector_size = 0
        self.mini_fat_sector_size = 0
        self.difat_first_sector = 0
        self.difat = []
        self.fat_sector_count = 0
        self.fat = []
        self.mini_fat = []
        self.mini_fat_first = 0
        self.first_dir_sector = 0
        self.directories = {}
        self.first_dir_sector = None
        self.mini_sector_cutoff = 4096

        self.header_bytes = []
        self.sat_bytes = []
        self.dir_bytes = []
        self.mini_fat_bytes = []

        self.data_frame_count = 0

        self.custom_props = {}

        current = io_stream.tell()
        io_stream.seek(0, os.SEEK_END)
        self.end = io_stream.tell()
        io_stream.seek(current)

        if not force_layer and io_stream.tell() == 0:
            # auto layer detection
            if self.read(4) == b'\xd0\xcf\x11\xe0':
                self.is_layer = True

            self.io_stream.seek(0)

        if self.is_layer and (  # pylint:disable=too-many-nested-blocks
                extract_doc_structure or parse_doc_structure_only):
            self._read_compound_header()
            self._build_sat()
            if not parse_doc_structure_only:
                if path:
                    dest_file = path
                elif 'Mx Document' in self.directories:
                    dest_file = 'Mx Document'
                elif 'Maps' in self.directories:
                    dest_file = 'Maps'
                elif 'PageLayout' in self.directories:
                    dest_file = 'PageLayout'
                elif 'Scene' in self.directories:
                    dest_file = 'Scene'
                elif 'Main Stream' in self.directories:
                    dest_file = 'Main Stream'
                elif 'Tool0' in self.directories:
                    dest_file = 'Tool0'
                else:
                    dest_file = 'Layer'

                if offset == -1:
                    if dest_file == 'Mx Document':
                        self.io_stream = self.extract_file_from_stream(dest_file)
                        self.read_int('unknown', expected=1)
                        self.read_int('unknown', expected=1)
                        self.read_int('unknown', expected=1)
                        self.data_frame_count = self.read_int('data frame count')
                    elif dest_file == 'Main Stream':
                        self.io_stream = self.extract_file_from_stream(dest_file)
                        self.read_int('unknown', expected=(1, 2))
                        self.data_frame_count = self.read_int('data frame count')
                    elif 'Tool' in dest_file:
                        self.io_stream = self.extract_file_from_stream(dest_file)
                        # version related?
                        self.read_int('unknown', expected=(1, 2))
                        self.read_ushort('unknown', expected=(1, 9))
                        self.read_ushort('unknown', expected=6)
                        self.read_stringv2('name')
                        self.read_stringv2('display name')
                        self.read_stringv2('description')
                        self.read_stringv2('path?')
                        self.read_int('tool id?')
                        self.read_stringv2('stylesheet')
                        self.read_ushort('store relative path names', expected=(0, 65535))
                        self.read_int('unknown', expected=0)
                        self.read_int('unknown', expected=0)

                    elif dest_file == 'Maps':
                        # first read prerequisites - in case references from these are
                        # used in map
                        templates_stream = self.extract_file_from_stream('Templates')
                        style_gallery_stream = self.extract_file_from_stream('StyleGallery')
                        if 'DrawingDefaults' in self.directories:
                            drawing_defaults_stream = self.extract_file_from_stream('DrawingDefaults')
                        else:
                            drawing_defaults_stream = None

                        maps_stream = self.extract_file_from_stream('Maps')

                        self.io_stream = templates_stream
                        count = self.read_int('template count')
                        for i in range(count):
                            self.read_string('template path {}'.format(i + 1))
                            self.read_int('unknown', expected=1)
                        self.read_int('unknown', expected=(3, 5))

                        if drawing_defaults_stream:
                            self.read_string('default font')
                            self.read_double('font size??', expected=(
                                0, 4.450147717014403e-308, 2061745644852025.5, 1.213859894000235e-304, 1.0699050853375465e+46))
                            string_count = self.read_int('string count???')
                            for i in range(string_count):
                                self.read_string('unknown string')
                                self.read_ushort('unknown', expected=(0, 65535))

                            self.read_string('toc current view mode',
                                             expected=(
                                                 'Display', 'Source', 'Selection', 'Visible', 'Layouts', 'Anzeige'))
                            self.read_object('selection environment')
                        else:
                            try:
                                self.read_object('default fill')
                                self.read_object('default line')
                                self.read_object('default marker')
                                self.read_object('default text symbol 1')
                                self.read_object('default text symbol 2')
                                self.read_object('default area patch')
                                self.read_object('default line patch')
                            except:  # nopep8, pylint: disable=bare-except
                                pass

                        self.io_stream = style_gallery_stream
                        self.read_object('style gallery')
                        if drawing_defaults_stream:
                            self.io_stream = drawing_defaults_stream
                            self.read_object('default fill')
                            self.read_object('default line')
                            self.read_object('default marker')
                            self.read_object('default text symbol 1')
                            self.read_object('default text symbol 2')
                            self.read_object('default area patch')
                            self.read_object('default line patch')

                        self.io_stream = maps_stream
                        self.data_frame_count = self.read_int('data frame count')
                        if self.data_frame_count == 0:
                            raise EmptyDocumentException()
                    else:
                        self.io_stream = self.extract_file_from_stream(dest_file)
                else:
                    self.io_stream = self.extract_file_from_stream(dest_file)
            else:
                io_stream.seek(current)

        if not self.io_stream:
            raise EmptyDocumentException()

        current = self.io_stream.tell()
        self.io_stream.seek(0, os.SEEK_END)
        self.end = self.io_stream.tell()
        self.io_stream.seek(current)

        if offset > 0:
            self.io_stream.seek(offset)

    def tell(self) -> int:
        """
        Returns the current position within the stream.
        """
        return self.io_stream.tell()

    def read(self, length: int) -> bin:
        """
        Reads the from the stream for the given length and returns
        the binary result.
        """
        return self.io_stream.read(length)

    def seek(self, offset: int):
        """
        Seeks for the given offset.
        """
        self.io_stream.seek(offset)

    def rewind(self, length):
        """
        Rewinds by the given length
        """
        self.io_stream.seek(self.io_stream.tell() - length)

    def log(self, message: str, offset: int = 0):
        """
        Logs a debug message
        """
        if self.debug:
            print('{}{} at {}'.format('   ' * self.debug_depth, message, hex(self.io_stream.tell() - offset)))

    def _read_compound_header(self):
        """
        Reads the document header
        """
        # magic identifier
        if not self.read(8) == b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1':
            raise DocumentTypeException()
        self.read(16)  # Unused clsid

        # not used -- just generic OLE stuff
        prev_debug = self.debug
        self.debug = False
        self.read_ushort('minor version')
        self.read_ushort('major version')
        self.read_ushort('bom')

        self.sector_size = 1 << self.read_ushort('Log(2) of fat sector size')
        self.log('sector size {}'.format(self.sector_size))
        self.mini_fat_sector_size = 1 << self.read_ushort('Log(2) of mini fat sector size')
        self.log('mini fat sector size {}'.format(self.mini_fat_sector_size))

        assert self.read_ushort('unused') == 0
        assert self.read_int('unused') == 0
        assert self.read_int('directory sector count') == 0
        self.fat_sector_count = self.read_int('fat sector count')
        self.first_dir_sector = self.read_int('first directory sector')
        self.read_int('unused', expected=(0, 2))  # seems like MXD doctor makes this a 2?

        self.mini_sector_cutoff = self.read_int('mini fact sector size cutoff')
        self.mini_fat_first = self.read_int('mini fat first sector')
        self.mini_fat_sector_count = self.read_int('mini fat sector count')
        self.difat_first_sector = self.read_int('difat first sector')
        self.difat_sector_count = self.read_int('difat sector count')

        self.header_size = max(self.sector_size, 512)
        self.max_sector = (self.end - max(self.sector_size, 512)) // self.sector_size

        self.debug = prev_debug

        for i in range(self.tell()):
            self.header_bytes.append(i)

    def _build_sat(self):  # pylint: disable=too-many-locals,too-many-branches,too-many-statements
        """
        Builds the various SAT tables
        """

        # first 109 entries follow the header
        self.difat = []
        start = self.tell()
        for i in range(109):
            s = self.read_int()
            if s not in (0xFFFFFFFE, 0xFFFFFFFF):
                self.difat.append(s)

        for i in range(start, self.tell()):
            self.sat_bytes.append(i)

        current_sector = self.difat_first_sector

        while current_sector not in (0xFFFFFFFE, 0xFFFFFFFF):
            offset = (current_sector + 1) * self.sector_size
            self.seek(offset)
            for _ in range(127):
                s = self.read_int()
                if s not in (0xFFFFFFFE, 0xFFFFFFFF):
                    self.difat.append(s)

            current_sector = self.read_int()

            for i in range(offset, self.tell()):
                self.sat_bytes.append(i)

        self.fat = []
        # read sectors in master sat to build up sat
        for sector in self.difat:
            offset = (sector + 1) * self.sector_size
            self.seek(offset)
            for _ in range(128):
                self.fat.append(self.read_int())

            for i in range(offset, self.tell()):
                self.sat_bytes.append(i)

        # mini fat
        self.mini_fat = []
        small_sat_stream = self._read_fat_stream(self.mini_fat_first, self.mini_fat_sector_count * self.sector_size)
        # TODO - use correct length!
        while True:
            try:
                self.mini_fat.append(unpack("<L", small_sat_stream.read(4))[0])
            except error:
                break
            except IndexError:
                break

        # extract directory listing
        current_sector = self.first_dir_sector
        # self.log('first dir sector {}'.format(current_sector))
        self.directories = {}
        self.mini_fat_first = None
        while current_sector >= 0:
            if current_sector in (0xFFFFFFFE, 0xFFFFFFFF):
                break

            offset = (current_sector + 1) * self.sector_size
            self.seek(offset)

            for i in range(4):
                name = self.read(64)
                entry_name_length = self.read_ushort()
                name = name[:entry_name_length - 2].decode('utf-16')
                self.log('found dir {}'.format(name))

                # self.log('found directory entry {}'.format(name))

                entry_type = self.read_uchar()  # 'entry type')  # type
                self.read_uchar()  # entry flags
                _ = self.read_int()  # left sibling
                _ = self.read_int()  # right sibling
                _ = self.read_int()  # root child
                self.read_raw_clsid()
                self.read_int()  # flags
                self.read(8)  # time
                self.read(8)  # time
                first_sector = self.read_int()  # first sector or short sector of stream
                stream_length = self.read_int()  # stream length low
                stream_length_high = self.read_int()  # stream length high
                if first_sector in (0xFFFFFFFE, 0xFFFFFFFF):
                    continue

                #                self.log('first sector {}'.format(first_sector))
                #                self.log('stream length low {}'.format(stream_length))
                # self.log('stream length high {}'.format(stream_length_high))

                assert stream_length_high == 0  # unhandled for now

                if self.mini_fat_first is None:
                    self.mini_fat_first = first_sector
                    self.mini_fat_size = stream_length

                if entry_type == 2:  # STGTY_Stream
                    self.directories[name] = ({'first_sector': first_sector,
                                               'stream_length': stream_length,
                                               'stream_length_high': stream_length_high
                                               })

            current_sector = self.fat[current_sector]
            for i in range(offset, self.tell()):
                self.dir_bytes.append(i)

    def _read_fat_stream(self, sector, length):
        """
        Reads a stream from FAT
        """
        current_sector = sector
        stream = BytesIO()
        read = 0
        while current_sector not in (0xFFFFFFFE, 0xFFFFFFFF):
            offset = (current_sector + 1) * self.sector_size
            self.seek(offset)
            to_read = min(self.sector_size, length - read)

            stream.write(self.read(to_read))
            read += self.sector_size

            current_sector = self.fat[current_sector]

            for i in range(offset, self.tell()):
                self.mini_fat_bytes.append(i)

        stream.seek(0)
        return stream

    def extract_file_from_stream(self, name):
        """
        Extracts a complete file binary from the stream
        """
        if name not in self.directories:
            return None

        directory = self.directories[name]
        stream_length = directory['stream_length']
        self.log('stream length {}'.format(stream_length))
        use_short_stream = stream_length < self.mini_sector_cutoff

        if use_short_stream:
            current_sector = self.mini_fat_first
            stream_length = self.mini_fat_size
        else:
            current_sector = directory['first_sector']

        # have to build the full binary, even if using short streams
        complete_sat_bin = BytesIO()
        read = 0
        while current_sector >= 0:
            if current_sector in (0xFFFFFFFE, 0xFFFFFFFF):
                break

            offset = (current_sector + 1) * self.sector_size
            self.seek(offset)
            to_read = min(self.sector_size, stream_length - read)

            complete_sat_bin.write(self.read(to_read))
            read += self.sector_size

            current_sector = self.fat[current_sector]

        complete_sat_bin.seek(0)

        if use_short_stream:
            self.log('using short stream')
            current_sector = directory['first_sector']
            stream_length = directory['stream_length']
            self.log('first sector {}'.format(current_sector))

            read = 0

            small_stream_bin = BytesIO()
            while current_sector not in (0xFFFFFFFE, 0xFFFFFFFF):
                offset = current_sector * self.mini_fat_sector_size
                complete_sat_bin.seek(offset)
                to_read = min(self.mini_fat_sector_size, stream_length - read)
                small_stream_bin.write(complete_sat_bin.read(to_read))

                read += self.mini_fat_sector_size
                current_sector = self.mini_fat[current_sector]

            small_stream_bin.seek(0)
            return small_stream_bin
        else:
            return complete_sat_bin

    def read_uchar(self, debug_string: str = '', expected=None) -> int:
        """
        Reads a uchar from the stream.
        """
        res = unpack("<B", self.io_stream.read(1))[0]
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
        """
        res = unpack("<d", self.io_stream.read(8))[0]
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
            res = unpack("<L", self.io_stream.read(4))[0]
        except error as e:  # struct.error
            raise UnreadableSymbolException('Truncated integer') from e

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
        res = unpack("<I", self.io_stream.read(4))[0]
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
        res = unpack("<i", self.io_stream.read(4))[0]
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
        res = unpack("<l", self.io_stream.read(4))[0]
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
        res = unpack("<H", self.io_stream.read(2))[0]
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
        clsid_bin = binascii.hexlify(self.io_stream.read(16))

        clsid = ObjectRegistry.hex_to_clsid2(clsid_bin)
        if debug_string and clsid != '00000000-0000-0000-0000-000000000000':
            self.log('Found {} clsid of {}'.format(debug_string, ObjectRegistry.hex_to_clsid(clsid_bin)), 16)
        return clsid

    def read_raw_clsid(self, debug_string: str = '', expected=None) -> str:
        """
        Reads a CLSID from the stream
        """
        clsid_bin = binascii.hexlify(self.io_stream.read(16))
        clsid = ObjectRegistry.hex_to_clsid(clsid_bin)
        if debug_string and clsid != '00000000-0000-0000-0000-000000000000':
            self.log('Found {} clsid of {}'.format(debug_string, clsid), 16)

        if not self.tolerant and expected is not None:
            if isinstance(expected, (tuple, list)):
                assert clsid in expected, 'Got {}, expected {}'.format(clsid, expected)
            else:
                assert clsid == expected, 'Got {}, expected {}'.format(clsid, expected)

        return clsid

    def read_string(self, debug_string: str = '', no_terminator=False, expected=None, size=None) -> str:
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
        if not no_terminator:
            buffer = self.io_stream.read(length - 2)
        else:
            buffer = self.io_stream.read(length)
        string = buffer.decode('utf-16')
        if not no_terminator:
            terminator = binascii.hexlify(self.io_stream.read(2))
        else:
            terminator = None
        if terminator is not None and terminator != b'0000':
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
            buffer = self.io_stream.read(length * 2)
            string = buffer.decode('utf-16')
            terminator = binascii.hexlify(self.io_stream.read(2))

            self.log('found string "{}"'.format(string))
            if terminator != b'0000':
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

        length = length if length is not None else unpack("<L", self.io_stream.read(4))[0]
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

    @staticmethod
    def _missing_elements(L):
        """
        Calculates missing elements from an incremental list
        """
        start, end = L[0], L[-1]
        return sorted(set(range(start, end + 1)).difference(L))

    def push_object_store(self):
        """
        Pushes a new object store to the stack
        """
        self.objects.append({})

    def pop_object_store(self):
        """
        Pops the last object store from the stack
        """
        del self.objects[-1]

    def read_object(self,  # pylint: disable=too-many-locals,too-many-branches,too-many-statements
                    debug_string: str = '',
                    allow_reference=True,
                    expect_existing=False,
                    expected_size=None) -> Optional[Object]:
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
        except UnknownClsidException as e:
            self.log(str(e), 16)

            self.log(str(self.unknown_objects))
            self.log(str(self.not_implemented_objects))

            if self.is_layer:
                this_ref = self.read_uint('ref id')
                self.rewind(4)
                self.unknown_objects[this_ref] = clsid

            raise e

        if res is not None:
            self.log('** {} **'.format(res.__class__.__name__), 16)
        else:
            self.log('{} not found'.format(debug_string), 16)

        if res is not None:
            self.debug_depth += 1

            this_ref = None
            if allow_reference and self.is_layer and res.supports_references():
                # chomp out reference id for lyr/mxd files
                self.current_ref_depth += 1
                this_ref = self.read_uint('ref id')

                if this_ref == 0 and res.compatible_versions() is None:
                    self.debug_depth -= 1
                    return res

                if this_ref in self.objects[-1]:
                    old_res = self.objects[-1][this_ref]
                    self.log('Retrieving existing object with ref {}: {}'.format(this_ref, old_res))
                    assert res.__class__ == old_res.__class__
                    self.debug_depth -= 1
                    return old_res
                elif expect_existing and not this_ref - 1 in self.objects[-1]:
                    self.log('Expecting an existing object with ref {}, but not yet created'.format(this_ref))
                    self.debug_depth -= 1
                    return None  # res
                elif not self.tolerant and self.objects[-1] and this_ref < max(self.objects[-1].keys()):
                    missing = self._missing_elements(list(self.objects[-1].keys()))
                    self.log(
                        'Encountered ref {}, but previously read ref {}. Likely a required object was skipped. Gaps at {}'.format(
                            this_ref, max(self.objects[-1].keys()), missing))

                    unknown_clsid = {ref: self.unknown_objects[ref] for ref in missing if ref in self.unknown_objects}
                    if unknown_clsid:
                        self.log('Unknown refs: {}'.format(str(unknown_clsid)))
                    not_implemented_clsid = {ref: self.not_implemented_objects[ref] for ref in missing if
                                             ref in self.not_implemented_objects}
                    if not_implemented_clsid:
                        self.log('Not implemented refs: {}'.format(str(not_implemented_clsid)))
                else:
                    self.log('storing {} as {}'.format(res.__class__.__name__, this_ref))
                    res.ref_id = this_ref
                    self.objects[-1][this_ref] = res

            version = 1
            try:
                compatible_versions = res.compatible_versions()
            except NotImplementedException as e:
                self.log('Compatible versions for {} are not yet implemented'.format(str(e)), 16)
                self.not_implemented_objects[this_ref] = res.__class__
                if this_ref:
                    del self.objects[-1][this_ref]
                raise e
            except PartiallyImplementedException as e:
                if expected_size is not None:
                    self.log('Reading {} is not fully implemented'.format(str(e)), 16)
                    self.not_implemented_objects[this_ref] = res.__class__
                    raise NotImplementedException(e) from e

                compatible_versions = None

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
                e.custom_object = res
                self.debug_depth -= 1
                raise e
            except NotImplementedException as e:
                self.log('Reading {} is not yet implemented'.format(str(e)), 16)
                self.not_implemented_objects[this_ref] = res.__class__
                raise e

            self.log('ended {}'.format(res.__class__.__name__))

            if self.debug:
                print('')
            self.debug_depth -= 1

        return res

    def read_embedded_file(self, debug_string: str = '') -> bin:
        """
        Reads an embedded file stored within the stream.
        """
        embedded_file_length = self.read_int('binary length')
        self.log('Found embedded file {} of length {}'.format(debug_string, embedded_file_length))
        try:
            return self.read(embedded_file_length)
        except error:  # struct.error
            raise UnreadableSymbolException('Truncated file binary') from error

    def read_variant(self,  # pylint: disable=too-many-branches
                     variant_type=None,
                     debug_string: str = '',
                     expected=None):
        """
        Reads a variant value from the stream
        """
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
            numeric = self.read_double('value')
            if numeric == 0:
                value = None
            else:
                value = datetime.strftime(
                    datetime(year=100, month=1, day=1) + timedelta(days=numeric + 657434),
                    '%Y-%m-%d %H:%M:%S')
        elif variant_type == Stream.USER_PASSWORD:
            length = self.read_uint('password length')
            value = '*' * length
            self.read(length)
        elif variant_type == Stream.VBDATAOBJECT:
            value = self.read_object('value')
        elif variant_type == 8197:  # esriAttributeTypeDash
            count = self.read_int('number of dashes')
            value = [self.read_double('value {}'.format(idx)) for idx in range(count)]
        else:
            raise UnreadableSymbolException('Unknown property type {}'.format(variant_type))

        if not self.tolerant and expected is not None:
            if isinstance(expected, (tuple, list)):
                assert value in expected, 'Got {}, expected {}'.format(value, expected)
            else:
                assert value == expected, 'Got {}, expected {}'.format(value, expected)

        return value

    def sniff_index_properties_header(self) -> bool:
        """
        Returns true if the next part of the stream is an indexed properties map
        """
        start = self.tell()
        res = self.read_ushort() in (250, 255, 34125) and self.read_ushort() in (255, 34419) and self.read_int() == 0
        self.seek(start)
        return res

    def read_indexed_properties(self, handler):
        """
        Reads an index property list from the stream, using the specified handler to parse it
        """
        self.log('starting indexed property parsing')

        # header
        self.read_ushort(expected=(250, 255, 34125))
        self.read_ushort(expected=(255, 4351, 34419))
        self.read_int(expected=0)

        while True:
            next_ref = self.read_int('reference')
            if next_ref == 0xffffffff:
                return
            else:
                size = self.read_int('size')
                handler(next_ref, size)
