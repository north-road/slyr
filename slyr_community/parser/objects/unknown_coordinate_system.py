#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class UnknownCoordinateSystem(Object):
    """
    UnknownCoordinateSystem
    """

    @staticmethod
    def cls_id():
        return "b286c06b-0879-11d2-aaca-00c04fa33c20"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.name = ""
        self.x_origin = None
        self.y_origin = None
        self.m_origin = None
        self.z_origin = None
        self.xy_resolution = None
        self.z_resolution = None
        self.m_resolution = None
        self.xy_tolerance = None
        self.z_tolerance = None
        self.m_tolerance = None
        self.is_high_precision = False

    @staticmethod
    def compatible_versions():
        return [1, 3]

    def read(self, stream: Stream, version):
        self.name = stream.read_string("name")
        stream.read_string("unknown")
        stream.read_string("unknown")
        stream.read_string("unknown")

        if version > 1:
            self.is_high_precision = (
                stream.read_ushort("is high precision", expected=(0, 1)) != 0
            )

        self.x_origin = stream.read_double("x origin")
        self.y_origin = stream.read_double("y origin")
        self.xy_resolution = stream.read_double("xy resolution")

        self.z_origin = stream.read_double("z origin")
        self.z_resolution = stream.read_double("z resolution")

        self.m_origin = stream.read_double("m origin")
        self.m_resolution = stream.read_double("m resolution")

        if version > 1:
            self.xy_tolerance = stream.read_double("xy tolerance")
            self.z_tolerance = stream.read_double("z tolerance")
            self.m_tolerance = stream.read_double("m tolerance")

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "name": self.name,
            "x_origin": self.x_origin,
            "y_origin": self.y_origin,
            "m_origin": self.m_origin,
            "z_origin": self.z_origin,
            "xy_resolution": self.xy_resolution,
            "z_resolution": self.z_resolution,
            "m_resolution": self.m_resolution,
            "xy_tolerance": self.xy_tolerance,
            "z_tolerance": self.z_tolerance,
            "m_tolerance": self.m_tolerance,
            "is_high_precision": self.is_high_precision,
        }
