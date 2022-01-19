#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class Indexes(Object):
    """
    Indexes
    """

    @staticmethod
    def cls_id():
        return '03859813-4da5-11d1-8824-0000f877762d'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.indexes = []

    def read(self, stream: Stream, version):
        count = stream.read_int('index count')
        for i in range(count):
            self.indexes.append(stream.read_object('index {}'.format(i + 1)))

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'indexes': [e.to_dict() if e is not None else None for e in self.indexes]
        }
