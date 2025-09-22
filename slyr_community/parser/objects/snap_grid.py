#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class SnapGrid(Object):
    """
    SnapGrid
    """

    @staticmethod
    def cls_id():
        return "31e081ad-cb02-11d1-876c-0000f8751720"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.visible = False

    def read(self, stream: Stream, version):
        self.visible = stream.read_ushort("visible") != 0
        stream.read_double("spacing hoz?")
        stream.read_double("spacing vert?")

    def to_dict(self):  # pylint: disable=method-hidden
        return {"visible": self.visible}
