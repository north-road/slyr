#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class FidSet(Object):
    """
    FidSet
    """

    @staticmethod
    def cls_id():
        return 'd79bdaf0-caa8-11d2-b2be-0000f878229e'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.fids = []

    def read(self, stream: Stream, version):
        count = stream.read_int('count')
        for i in range(count):
            self.fids.append(stream.read_int('fid {}'.format(i + 1)))

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'fids': self.fids
        }
