#!/usr/bin/env python
"""
Serializable object subclass

COMPLETE INTERPRETATION
"""

import math
from ..object import Object
from ..stream import Stream


class IlluminationProps(Object):
    """
    IlluminationProps
    """

    @staticmethod
    def cls_id():
        return "1c352f40-298e-11d3-9f4f-00c04f6bc619"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.contrast = 3
        self.sun_x = 0
        self.sun_y = 0
        self.sun_z = 0
        self.altitude = 0
        self.azimuth = 0

    def read(self, stream: Stream, version):
        self.sun_x = stream.read_double("sun x")
        self.sun_y = stream.read_double("sun y")
        self.sun_z = stream.read_double("sun z")
        self.altitude = math.degrees(math.asin(self.sun_z))
        self.contrast = stream.read_double("contrast")
        self.azimuth = 90 - math.degrees(math.atan2(self.sun_y, self.sun_x))

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "contrast": self.contrast,
            "altitude": self.altitude,
            "azimuth": self.azimuth,
            "sun_x": self.sun_x,
            "sun_y": self.sun_y,
            "sun_z": self.sun_z,
        }
