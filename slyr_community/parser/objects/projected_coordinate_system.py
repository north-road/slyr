#!/usr/bin/env python
"""
Serializable object subclass

PARTIAL INTERPRETATION -- some unknown content, not robust

"""

from ..object import Object
from ..stream import Stream


class ProjectedCoordinateSystem(Object):
    """
    ProjectedCoordinateSystem
    """

    @staticmethod
    def cls_id():
        return "2a626700-1dd2-11b2-bf51-08002022f573"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.wkt = None
        self.x_origin = None
        self.y_origin = None
        self.m_origin = None
        self.z_origin = None
        self.xy_scale = None
        self.m_scale = None
        self.z_scale = None
        self.xy_tolerance = None
        self.z_tolerance = None
        self.m_tolerance = None
        self.is_high_precision = False

    @staticmethod
    def compatible_versions():
        return [1, 2, 3, 6, 7]

    def read(self, stream: Stream, version):
        self.wkt = stream.read_ascii("wkt")

        if version > 1:
            if version < 7:
                stream.read_double("unknown")
                size = stream.read_int("unknown size")
                stream.read(size)
                stream.read_int("unknown", expected=0)

            if stream.read_uchar("unknown", expected=(0, 1)) != 0:
                stream.read_ushort("unknown", expected=1)
                stream.read_ascii("vertical unit??")

        if version > 3:
            self.is_high_precision = (
                stream.read_ushort("is high precision", expected=(0, 1)) != 0
            )

        if version > 2:
            self.x_origin = stream.read_double("x origin")
            self.y_origin = stream.read_double("y origin")
            self.xy_scale = stream.read_double("xy scale")

            self.z_origin = stream.read_double("z origin")
            self.z_scale = stream.read_double("z scale")

            self.m_origin = stream.read_double("m origin")
            self.m_scale = stream.read_double("m scale")

        if version > 3:
            self.xy_tolerance = stream.read_double("xy tolerance")
            self.z_tolerance = stream.read_double("z tolerance")
            self.m_tolerance = stream.read_double("m tolerance")

        if version > 6:
            stream.read_double("k")
            stream.read_double("l")

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "wkt": self.wkt,
            "x_origin": self.x_origin,
            "y_origin": self.y_origin,
            "m_origin": self.m_origin,
            "z_origin": self.z_origin,
            "xy_scale": self.xy_scale,
            "m_scale": self.m_scale,
            "z_scale": self.z_scale,
            "xy_tolerance": self.xy_tolerance,
            "z_tolerance": self.z_tolerance,
            "m_tolerance": self.m_tolerance,
            "is_high_precision": self.is_high_precision,
        }

    @classmethod
    def from_dict(cls, definition: dict) -> "ProjectedCoordinateSystem":
        res = ProjectedCoordinateSystem()
        res.wkt = definition["wkt"]
        res.x_origin = definition["x_origin"]
        res.y_origin = definition["y_origin"]
        res.m_origin = definition["m_origin"]
        res.z_origin = definition["z_origin"]
        res.xy_scale = definition["xy_scale"]
        res.m_scale = definition["m_scale"]
        res.z_scale = definition["z_scale"]
        res.xy_tolerance = definition["xy_tolerance"]
        res.z_tolerance = definition["z_tolerance"]
        res.m_tolerance = definition["m_tolerance"]
        res.is_high_precision = definition.get("is_high_precision", False)
        return res
