#!/usr/bin/env python
"""
Serializable object subclass
"""

from ...parser.object import Object
from ...parser.stream import Stream


class LODInfo(Object):
    """
    LODInfo
    """

    @staticmethod
    def cls_id():
        return "35bd0f76-3cf3-4d0c-9c4a-d728cfe593a5"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.level = 1
        self.scale = 0
        self.resolution = 0

    def read(self, stream: Stream, version):
        self.level = stream.read_int("level")
        self.scale = stream.read_double("scale?")
        self.resolution = stream.read_double("resolution?")

    def to_dict(self):  # pylint: disable=method-hidden
        return {"level": self.level, "scale": self.scale, "resolution": self.resolution}
