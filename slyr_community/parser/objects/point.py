#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class Point(Object):
    """
    Point
    """

    @staticmethod
    def cls_id():
        return "00a5cb41-52da-11d0-a8f2-00608c85ede5"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.x = 0
        self.y = 0
        self.z = None
        self.m = None
        self.crs = None

    @staticmethod
    def compatible_versions():
        return [2]

    def read(self, stream: Stream, version):
        size = stream.read_int("size")
        start = stream.tell()
        point_type = stream.read_int("point type")

        self.x = stream.read_double("x")
        self.y = stream.read_double("y")
        if point_type in (9, 11):
            self.z = stream.read_double("z")
        if point_type in (11, 21):
            self.m = stream.read_double("m")

        assert stream.tell() == size + start, (size, stream.tell() - start)

        self.crs = stream.read_object("crs")

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "m": self.m,
            "crs": self.crs.to_dict() if self.crs else None,
        }
