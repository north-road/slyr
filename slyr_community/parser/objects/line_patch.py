#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class LinePatch(Object):
    """
    LinePatch
    """

    @staticmethod
    def cls_id():
        return "2066267f-e3b8-11d2-b868-00600802e603"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.polyline = None
        self.name = ""
        self.preserve_aspect = False

    @staticmethod
    def compatible_versions():
        return [2, 3]

    def read(self, stream: Stream, version):
        self.polyline = stream.read_object("polyline")
        self.name = stream.read_string("name")
        self.preserve_aspect = stream.read_ushort("preserve aspect") != 0

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "polyline": self.polyline.to_dict() if self.polyline else None,
            "name": self.name,
            "preserve_aspect": self.preserve_aspect,
        }
