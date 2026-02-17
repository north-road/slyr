#!/usr/bin/env python
"""
Serializable object subclass
"""

from ...parser.object import Object
from ...parser.stream import Stream


class TileImageInfo(Object):
    """
    TileImageInfo
    """

    @staticmethod
    def cls_id():
        return "0ca787d5-fcae-412d-85d8-61aa304b1ae1"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.format = "*"
        self.description = ""
        self.attribution = ""

    @staticmethod
    def compatible_versions():
        return None

    def read(self, stream: Stream, version):
        self.format = stream.read_string("format")  # '*', 'PNG', 'Mixed'
        stream.read_int("unknown", expected=0)  # compression?

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "format": self.format,
            "description": self.description,
            "attribution": self.attribution,
        }
