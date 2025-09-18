#!/usr/bin/env python
"""
Serializable object subclass
"""

from .geometry import Geometry
from ..stream import Stream


class Multipoint(Geometry):
    """
    Multipoint
    """

    @staticmethod
    def cls_id():
        return "00a5cb40-52da-11d0-a8f2-00608c85ede5"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.points = []

    @staticmethod
    def compatible_versions():
        return [2]

    def read(self, stream: Stream, version):
        size = stream.read_int("size")
        start = stream.tell()
        stream.read_int("wkb type?", expected=8)

        self.x_min = stream.read_double("x min")
        self.y_min = stream.read_double("y min")
        self.x_max = stream.read_double("x max")
        self.y_max = stream.read_double("y max")

        count = stream.read_int("count")
        for i in range(count):
            x = stream.read_double("x {}".format(i + 1))
            y = stream.read_double("y {}".format(i + 1))
            self.points.append([x, y])

        # likely here:
        # - if wkb type is 18 we need to read two doubles of z min/max, then
        #   an array of z values
        # - if wkb type is 18 or 28  we need to read two doubles of m min/max,
        #   then an array of m values

        assert stream.tell() == size + start, (stream.tell(), size + start)
        self.crs = stream.read_object("crs")

    def to_dict(self):  # pylint: disable=method-hidden
        res = super().to_dict()
        res["points"] = self.points
        return res
