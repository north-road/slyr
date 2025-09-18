#!/usr/bin/env python
"""
Serializable object subclass

NEAR COMPLETE INTERPRETATION -- robust but some unknown content
"""

from ..object import Object
from ..stream import Stream


class Envelope(Object):
    """
    Envelope
    """

    @staticmethod
    def cls_id():
        return "30707212-52d5-11d0-a8f2-00608c85ede5"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.x_min = 0.0
        self.x_max = 0.0
        self.y_min = 0.0
        self.y_max = 0.0
        self.has_z = False
        self.has_m = False
        self.z_min = 0
        self.z_max = 0
        self.m_min = 0
        self.m_max = 0
        self.crs = None

    @staticmethod
    def compatible_versions():
        return [3]

    def read(self, stream: Stream, version):
        self.x_min = stream.read_double("x min")
        self.y_min = stream.read_double("y min")
        self.x_max = stream.read_double("x max")
        self.y_max = stream.read_double("y max")
        res = stream.read_int("unknown")
        if res == 128:
            self.has_z = True
            self.z_min = stream.read_double("z min")
            self.z_max = stream.read_double("z max")
        elif res == 64:
            self.has_m = True
            self.m_min = stream.read_double("m min")
            self.m_max = stream.read_double("m max")
        elif res == 192:
            self.has_z = True
            self.has_m = True
            self.m_min = stream.read_double("m min")
            self.m_max = stream.read_double("m max")
            self.z_min = stream.read_double("z min")
            self.z_max = stream.read_double("z max")
        else:
            assert res == 0, res

        self.crs = stream.read_object("crs")

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "x_min": self.x_min,
            "x_max": self.x_max,
            "y_min": self.y_min,
            "y_max": self.y_max,
            "crs": self.crs.to_dict() if self.crs else None,
        }
