#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..stream import Stream
from .raster_renderer import RasterRenderer


class RasterColorMapRenderer(RasterRenderer):
    """
    RasterColorMapRenderer
    """

    @staticmethod
    def cls_id():
        return "3b8283fa-1bd4-4212-b385-19e77b9e0d3b"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.groups = []
        self.values = []

    @staticmethod
    def compatible_versions():
        return [1, 2, 3]

    def read(self, stream: Stream, version):
        stream.read_ushort("unknown", expected=0)

        count = stream.read_int("group count")
        for i in range(count):
            self.groups.append(stream.read_object("legend group {}".format(i + 1)))

        count = stream.read_int("colors count?")
        for i in range(count):
            self.values.append(stream.read_int("value {}".format(i + 1)))

        super().read(stream, version)

        if version > 2:
            stream.read_double("unknown", expected=0)
            stream.read_int("unknown", expected=count - 1 if count else 255)
        elif version > 1:
            stream.read_int("unknown", expected=0)

    def to_dict(self):  # pylint: disable=method-hidden
        res = super().to_dict()
        res["values"] = self.values
        res["groups"] = [g.to_dict() for g in self.groups]
        return res
