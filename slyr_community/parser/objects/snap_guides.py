#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class SnapGuides(Object):
    """
    SnapGuides
    """

    @staticmethod
    def cls_id():
        return "31e081ae-cb02-11d1-876c-0000f8751720"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.guides = []

    def read(self, stream: Stream, version):
        count = stream.read_int("count")
        for i in range(count):
            self.guides.append(stream.read_double("guide {}".format(i + 1)))
        stream.read_ushort("visible??")  # , expected=65535)
        stream.read_int("draw level??", expected=32)

    def to_dict(self):  # pylint: disable=method-hidden
        return {"guides": self.guides}
