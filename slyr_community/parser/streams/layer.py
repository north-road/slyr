#!/usr/bin/env python
"""
Representation of a LYR file structure
"""

import os

from ..exceptions import (
    EmptyDocumentException,
    DocumentTypeException
)
from ..stream import Stream


class LayerFile:
    """
    Represents a LYR file structure
    """

    def __init__(self, io_stream, debug: bool = False, offset: int = 0, tolerant=True, check_length=False):

        if io_stream.read(4) != b'\xd0\xcf\x11\xe0':
            raise DocumentTypeException()

        io_stream.seek(io_stream.tell() - 4)

        stream = Stream(io_stream, debug=debug, offset=offset, force_layer=True, extract_doc_structure=True,
                        tolerant=tolerant, parse_doc_structure_only=True, path='Layer')

        if not stream.directories:
            raise EmptyDocumentException()

        layer_stream = stream.extract_file_from_stream('Layer')

        stream.io_stream = layer_stream
        self.root = stream.read_object()
        if check_length:
            pos = stream.io_stream.tell()
            stream.io_stream.seek(0, os.SEEK_END)
            assert pos == stream.io_stream.tell(), 'Did not read to end of Layer stream. Read to {} of {}'.format(
                hex(pos), hex(stream.io_stream.tell()))

    def to_dict(self):  # pylint: disable=method-hidden,missing-function-docstring
        return {
            'root': self.root.to_dict() if self.root else None
        }
