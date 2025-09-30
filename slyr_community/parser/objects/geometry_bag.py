#!/usr/bin/env python
"""
Serializable object subclass
"""

from .geometry import Geometry
from ..stream import Stream


class GeometryBag(Geometry):
    """
    GeometryBag
    """

    @staticmethod
    def cls_id():
        return "10b5f5c0-3781-11d2-bcc5-0000f875bcce"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.envelope = None
        self.geometries = []
        self.crs = None

    def read(self, stream: Stream, version):
        count = stream.read_int("count")
        self.envelope = stream.read_object("envelope")

        for i in range(count):
            self.geometries.append(stream.read_object("geometry {}".format(i + 1)))

        self.crs = stream.read_object("crs")
        stream.read_uchar("unknown", expected=0)

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "envelope": self.envelope.to_dict() if self.envelope else None,
            "crs": self.crs.to_dict() if self.crs else None,
            "geometries": [g.to_dict() for g in self.geometries],
        }
