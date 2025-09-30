#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class MapInset(Object):
    """
    MapInset
    """

    @staticmethod
    def cls_id():
        return "7a3f91e3-b9e3-11d1-8756-0000f8751720"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.name = ""
        self.map = None
        self.is_live = False
        self.fixed_aspect_ratio = False
        self.zoom_percent = 0
        self.zoom_scale = 0
        self.reference_scale = 0
        self.map_bounds = None
        self.maximum_extent_shown = None

    @staticmethod
    def compatible_versions():
        return [2]

    def read(self, stream: Stream, version):
        stream.read_ushort("unknown", expected=3)
        self.name = stream.read_string("name")
        self.map = stream.read_object("map")
        self.fixed_aspect_ratio = stream.read_ushort("fixed aspect ratio") != 0

        stream.read_int("unknown", expected=1)
        stream.read_int("unknown", expected=2146959360)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=1)

        self.zoom_percent = stream.read_double("zoom percent")
        self.zoom_scale = stream.read_double("zoom scale")

        self.is_live = stream.read_ushort("is live") != 0
        stream.read_ushort("is live again", expected=self.is_live)

        self.map_bounds = stream.read_object("map bounds")
        stream.read_object("unknown envelope")

        self.reference_scale = stream.read_double("reference scale")

        self.maximum_extent_shown = stream.read_object("maximum extent shown")

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "name": self.name,
            "map": self.map,
            "is_live": self.is_live,
            "fixed_aspect_ratio": self.fixed_aspect_ratio,
            "zoom_percent": self.zoom_percent,
            "zoom_scale": self.zoom_scale,
            "reference_scale": self.reference_scale,
            "map_bounds": self.map_bounds.to_dict() if self.map_bounds else None,
            "maximum_extent_shown": self.maximum_extent_shown.to_dict()
            if self.maximum_extent_shown
            else None,
        }
