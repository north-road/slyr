#!/usr/bin/env python
"""
Embedded pictures

COMPLETE INTERPRETATION
"""

import binascii
import struct
import base64
from slyr_community.parser.object import Object
from slyr_community.parser.exceptions import UnreadablePictureException
from slyr_community.parser.stream import Stream


class Picture(Object):
    """
    A Picture object. Note that picture objects are not associated with a CLSID
    and cannot be automatically read from a stream!
    """

    def __init__(self):  # pylint: disable=useless-super-delegation
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
            else:  # if pic_type in (1, 2, 35, 1092026755, 2147489655, 3244589537, 3244686334, 3244689366):
                pic = BmpPicture()
            # else:
            #     raise UnreadablePictureException('Unknown picture type {}'.format(pic_type))

            pic.read(stream, pic_type)
        elif version == 3:
            pic = stream.read_object('picture')
        else:
            raise UnreadablePictureException('Unknown picture version {}'.format(version))
        return pic

    def to_dict(self):
        return {
            'type': self.__class__.__name__,
            'content': base64.b64encode(self.content)
        }


class StdPicture(Object):
    """
    Standard OLE picture
    """

    @staticmethod
    def cls_id():
        return '0be35204-8f91-11ce-9de3-00aa004bb851'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.picture = None

    @staticmethod
    def compatible_versions():
        return None

    def to_dict(self):
        return {
            'picture_type': None if self.picture is None else self.picture.__class__.__name__,
            'content': base64.b64encode(self.picture.content)
        }

    def children(self):
        res = super().children()
        if self.picture:
            res.append(self.picture)
        return res

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

    FORMAT_BMP = 0
    FORMAT_PNG = 1
    FORMAT_EMF = 2
    FORMAT_JPG = 3

    def __init__(self):
        super().__init__()
        self.format = None

    def read(self, stream, version):
        """
        Reads the object from the given stream
        """
        stream.log('Reading pixmap of type {}'.format(version))
        self.content = self.read_from_stream(stream)

    def read_from_stream(self, stream: Stream):
        size = stream.read_uint('Pixmap size')

        check = stream.read(2)
        if check == b'BM':
            # BMP file
            # next bit should be size again
            size2 = struct.unpack("<I", stream.read(4))[0]
            if size != size2:
                raise UnreadablePictureException(
                    'Bitmap size {} did not match size in header {}'.format(size, size2))
            self.format = BmpPicture.FORMAT_BMP
            stream.rewind(6)
            return stream.read(size)
        elif check == b'\x01\x00':
            # EMF file
            stream.rewind(2)
            self.format = BmpPicture.FORMAT_EMF
            return stream.read(size)
        elif check == b'\xff\xd8':
            # JPG file
            check = stream.read(1)
            assert check == b'\xff'
            stream.rewind(3)
            self.format = BmpPicture.FORMAT_JPG
            return stream.read(size)
        elif check == b'\x89\x50':
            # PNG file
            start = stream.tell() - 2
            if stream.read(6) != b'\x4e\x47\x0d\x0a\x1a\x0a':  # where is 0d?
                raise UnreadablePictureException('Corrupt PNG header')

            first = True
            while True:
                chunk_start = stream.tell()
                chunk_size = struct.unpack(">I", stream.read(4))[0]
                chunk_type = stream.read(4)
                if first:
                    if not chunk_type == b'IHDR':
                        raise UnreadablePictureException('Missing PNG IHDR chunk')
                    first = False
                stream.read(chunk_size)
                stream.read(4)  # CRC
                if chunk_type == b'IEND':
                    break

            found_size = stream.tell() - start
            if size != found_size:
                raise UnreadablePictureException(
                    'PNG size {} did not match size in header {}'.format(found_size, size))
            self.format = BmpPicture.FORMAT_PNG
            stream.seek(start)
            return stream.read(found_size)
        else:
            stream.rewind(2)
            raise UnreadablePictureException('Expected 424d (\'BM\'), got {}'.format(check))

    def read_binary(self, content: bin):
        """
        Reads the bitmap from binary content
        """

        # some checks to verify that we've hit a BMP header
        check = binascii.hexlify(content[:2])
        if check == b'424d':
            # BMP file
            # next bit should be size again
            size2 = struct.unpack("<I", content[2:6])[0]
            if len(content) != size2:
                raise UnreadablePictureException(
                    'Bitmap size {} did not match size in header {}'.format(len(content), size2))
            self.format = BmpPicture.FORMAT_BMP
        elif binascii.hexlify(content[:4]) == b'89504e47':
            # PNG file

            self.format = BmpPicture.FORMAT_PNG
        elif check == check == b'\x01\x00':
            # EMF file
            self.format = BmpPicture.FORMAT_EMF
        else:
            raise UnreadablePictureException('Expected 424d (\'BM\'), got {}'.format(check))

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
