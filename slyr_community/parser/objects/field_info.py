#!/usr/bin/env python
"""
FieldInfo

Contains field properties
COMPLETE INTERPRETATION
"""

import binascii
from ..object import Object
from ..stream import Stream


class FieldInfo(Object):
    """
    Field Info
    """

    @staticmethod
    def cls_id():
        return 'a2baae2d-969b-11d2-ae77-080009ec732a'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.alias = ''
        self.number_format = None
        self.visible = True
        self.value_as_ratio = False
        self.highlight = False
        self.read_only = False

    @staticmethod
    def compatible_versions():
        return [1, 2, 3, 4]

    def read(self, stream: Stream, version):
        self.visible = stream.read_ushort('visible') != 0
        if version > 1:
            self.value_as_ratio = stream.read_ushort('value as ratio') != 0

        self.alias = stream.read_string('alias')
        self.number_format = stream.read_object('format')
        if version >= 3:

            if version >= 4:
                stream.read_ushort('unknown', expected=(0, 65535))
                stream.read_ushort('annotation related?', expected=(0,65535))
            stream.read_ushort('annotation related?', expected=(0,65535))

            self.highlight = stream.read_ushort('highlight') != 0
            self.read_only = stream.read_ushort('read only') != 0

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'alias': self.alias,
            'number_format': self.number_format.to_dict() if self.number_format else None,
            'visible': self.visible,
            'highlight': self.highlight,
            'read_only': self.read_only,
            'value_as_ratio': self.value_as_ratio
        }
