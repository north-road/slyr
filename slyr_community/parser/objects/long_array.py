#!/usr/bin/env python
"""
SymbolBackground

"""

from ..object import Object
from ..stream import Stream


class LongArray(Object):
    """
    LongArray
    """

    @staticmethod
    def cls_id():
        return "98bfb808-e91f-11d2-9f81-00c04f8ece27"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.values = []

    def read(self, stream: Stream, version):
        count = stream.read_int("count")
        for i in range(count):
            self.values.append(stream.read_int("value {}".format(i + 1)))

    def to_dict(self):  # pylint: disable=method-hidden
        return {"values": self.values}
