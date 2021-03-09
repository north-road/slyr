#!/usr/bin/env python
"""
Serializable object subclass
"""

from slyr_community.parser.object import Object
from slyr_community.parser.stream import Stream


class MultiPatch(Object):
    """
    MultiPatch
    """

    @staticmethod
    def cls_id():
        return 'f3c041c6-ae4d-11d2-9c93-00c04fb17838'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.crs = None

    @staticmethod
    def compatible_versions():
        return [1, 2]

    def read(self, stream: Stream, version):
        size = stream.read_int('size')
        # TODO - reverse engineer
        stream.read(size)

        self.crs = stream.read_object('crs')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'crs': self.crs.to_dict() if self.crs else None
        }
