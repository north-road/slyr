#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class Names(Object):
    """
    Names
    """

    @staticmethod
    def cls_id():
        return "e141c7af-1c30-4b67-99a1-2ddd2ff2c04d"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.names = []

    def read(self, stream: Stream, version):
        count = stream.read_int("count")
        for i in range(count):
            self.names.append(stream.read_string("name {}".format(i + 1)))

    def to_dict(self):  # pylint: disable=method-hidden
        return {"names": self.names}
