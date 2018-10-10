#!/usr/bin/env python
"""
std OLE Font
"""

import binascii
import struct
from slyr.parser.object import Object
from slyr.parser.exceptions import (UnknownPictureTypeException,
                                    UnreadablePictureException)


class Picture(Object):
    """
    A Picture object. Note that picture objects are not associated with a GUID
    and cannot be automatically read from a stream!
    """

    def __init__(self):
        super().__init__()
        self.content = None

    @staticmethod
    def create_from_bytes(content: bin) -> 'Picture':
        """
        Creates a picture directly from a binary blob, sniffing out the correct
        picture type.
        """
        # sniff the first couple of bytes to check for picture type
        if binascii.hexlify(content[:2]) == b'424d':
            # bitmap
            pic = BmpPicture()
            pic.read_binary(content)
        elif binascii.hexlify(content[:4]) == b'01000000':
            pic = EmfPicture()
            pic.read_binary(content)
        else:
            raise UnreadablePictureException('Could not sniff picture type')

        return pic

    @staticmethod
    def create_from_stream(stream) -> 'Picture':
        """
        Reads a picture from the stream and returns it
        """
        version = stream.read_uint('version')
        pic_type = stream.read_uint('pic_type')

        if version == 2:
            if pic_type == 0:
                pic = EmfPicture()
            elif pic_type == 1:
                pic = BmpPicture()
            else:
                raise UnknownPictureTypeException('Unknown picture type {}'.format(pic_type))

            pic.read(stream, 1)
        elif version == 3:
            pic = stream.read_object('picture')
        else:
            raise UnreadablePictureException('Unknown picture version {}'.format(version))
        return pic


class StdPicture(Object):
    """
    Standard OLE picture
    """

    def __init__(self):
        super().__init__()
        self.picture = None

    @staticmethod
    def guid():
        return '0be35204-8f91-11ce-9de3-00aa004bb851'

    @staticmethod
    def compatible_versions():
        return None

    def read(self, stream, version):
        constant = stream.read_ulong()
        if constant != 0x0000746C:
            raise UnreadablePictureException('Could not read StdPicture constant, got {}'.format(hex(constant)))
        size = stream.read_ulong('size')

        # next bit is the picture
        content = stream.read(size)
        self.picture = Picture.create_from_bytes(content)


class BmpPicture(Picture):
    """
    A standard windows BMP picture
    """

    def read(self, stream, _):
        """
        Reads the object from the given stream
        """
        stream.log('Reading BMP file')
        size = stream.read_uint('BMP size')

        content = stream.read(size)
        self.read_binary(content)

    def read_binary(self, content: bin):
        """
        Reads the bitmap from binary content
        """

        # some checks to verify that we've hit a BMP header
        check = binascii.hexlify(content[:2])
        if check != b'424d':
            raise UnreadablePictureException('Expected 424d (\'BM\'), got {}'.format(check))

        # next bit should be size again
        size2 = struct.unpack("<I", content[2:6])[0]
        if len(content) != size2:
            raise UnreadablePictureException(
                'Bitmap size {} did not match size in header {}'.format(len(content), size2))

        # all good! rewind and store bitmap
        self.content = content


class EmfPicture(Picture):
    """
    An EMF/WMF picture
    """

    def read(self, stream, _):
        """
        Reads the object from the given stream
        """
        stream.log('Reading EMF file')
        size = stream.read_uint('EMF size')

        content = stream.read(size)
        self.read_binary(content)

    def read_binary(self, content: bin):
        """
        Reads the EMF from binary content
        """

        # some checks to verify that we've hit a EMF header
        check = binascii.hexlify(content[:4])
        if check != b'01000000':
            raise UnreadablePictureException('Expected EMF header 010000000, got {}'.format(check))

        # all good! rewind and store bitmap
        self.content = content
