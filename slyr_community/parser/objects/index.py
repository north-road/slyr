#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class Index(Object):
    """
    Index
    """

    @staticmethod
    def cls_id():
        return '826e2701-4da6-11d1-8824-0000f877762d'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.name = ''
        self.is_unique = False
        self.is_ascending = False
        self.fields = None

    def read(self, stream: Stream, version):
        stream.read_ushort('unknown', expected=1)
        stream.read_ushort('unknown', expected=65535)

        self.name = stream.read_string('name')

        stream.read_uchar('unknown', expected=1)

        self.is_unique = stream.read_uchar('is unique') != 0
        self.is_ascending = stream.read_uchar('is ascending') != 0
        self.fields = stream.read_object('fields')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'name': self.name,
            'is_unique': self.is_unique,
            'is_ascending': self.is_ascending,
            'fields': self.fields.to_dict() if self.fields else None,
        }
