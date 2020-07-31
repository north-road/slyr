#!/usr/bin/env python
"""
Serializable object subclass
"""

from slyr_community.parser.object import Object, not_implemented
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

    @staticmethod
    def compatible_versions():
        return [2]

    def read(self, stream: Stream, version):
        size = stream.read_int('size')
        # TODO - reverse engineer
        stream.read(size)
        return

    def to_dict(self):
        return {
        }
