#!/usr/bin/env python
"""
Serializable object subclass

PARTIAL INTERPRETATION -- some unknown content, may not be robust

"""

from ..object import Object
from ..stream import Stream


class TransparencyDisplayFilter(Object):
    """
    TransparencyDisplayFilter
    """

    @staticmethod
    def cls_id():
        return 'ad754a65-13b4-11d3-b89d-00600802e603'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.opacity = 255

    def read(self, stream: Stream, version):
        self.opacity = stream.read_ushort('opacity')  # 0 - 255
        stream.read_ushort('unknown', expected=1)  # maybe display filter flag?
        stream.read(8)  # == b'\x00\x00\x00\xdd\x00\x00\x00\x00'

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'opacity': self.opacity
        }
