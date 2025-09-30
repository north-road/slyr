#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class LocatorRectangle(Object):
    """
    LocatorRectangle
    """

    @staticmethod
    def cls_id():
        return "83ffcae2-edca-11d0-8683-0000f8751720"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.map = None
        self.border = None
        self.background = None
        self.callout = None
        self.show_leader = False
        self.shadow = None
        self.use_simple_extent = False

    @staticmethod
    def compatible_versions():
        return [2, 3]

    def read(self, stream: Stream, version):
        self.map = stream.read_object("map frame")
        self.border = stream.read_object("border")
        self.background = stream.read_object("background")
        self.callout = stream.read_object("callout line symbol")
        self.show_leader = stream.read_ushort("show leader") != 0
        self.shadow = stream.read_object("shadow")

        if version > 2:
            self.use_simple_extent = stream.read_ushort("use simple extent") != 0

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "map": str(self.map) if self.map else None,
            "border": self.border.to_dict() if self.border else None,
            "background": self.background.to_dict() if self.background else None,
            "callout": self.callout.to_dict() if self.callout else None,
            "show_leader": self.show_leader,
            "shadow": self.shadow.to_dict() if self.shadow else None,
            "use_simple_extent": self.use_simple_extent,
        }
