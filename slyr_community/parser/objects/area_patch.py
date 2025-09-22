#!/usr/bin/env python
"""
Serializable object subclass

COMPLETE INTERPRETATION
"""

from ..object import Object
from ..stream import Stream


class AreaPatch(Object):
    """
    AreaPatch
    """

    @staticmethod
    def cls_id():
        return "2066267e-e3b8-11d2-b868-00600802e603"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.polygon = None
        self.name = ""
        self.preserve_aspect = False

    @staticmethod
    def compatible_versions():
        return [2, 3]

    def read(self, stream: Stream, version):
        self.polygon = stream.read_object("polygon")
        self.name = stream.read_string("name")
        self.preserve_aspect = stream.read_ushort("preserve aspect") != 0

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "polygon": self.polygon.to_dict() if self.polygon else None,
            "name": self.name,
            "preserve_aspect": self.preserve_aspect,
        }
