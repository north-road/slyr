#!/usr/bin/env python
"""
Serializable object subclass

NEAR COMPLETE INTERPRETATION -- some unknown content, but should be robust
"""

import math
from ..object import Object
from ..stream import Stream


class GeographicCoordinateSystem(Object):
    """
    GeographicCoordinateSystem
    """

    @staticmethod
    def cls_id():
        return 'a6a87a80-1dd1-11b2-bf51-08002022f573'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.wkt = ''
        self.x_origin = 0
        self.y_origin = 0
        self.xy_scale = 0
        self.z_origin = 0
        self.z_scale = 0
        self.m_origin = 0
        self.m_scale = 0
        self.xy_tolerance = 0
        self.z_tolerance = 0
        self.m_tolerance = 0
        self.is_high_precision = False

    @staticmethod
    def compatible_versions():
        return [1, 3, 4, 7]

    def read(self, stream: Stream, version):
        self.wkt = stream.read_ascii('wkt')
        if version > 1:
            stream.read_int('unknown', expected=0)
            stream.read_int('unknown', expected=0)
            stream.read_uchar('unknown', expected=0)
            stream.read_double('unknown', expected=0)

            stream.read_double('x min?')
            stream.read_double('x max?')

        if version > 4:
            self.is_high_precision = stream.read_ushort('is high precision', expected=(0, 1)) != 0

        if version > 3:
            self.x_origin = stream.read_double('x origin')
            self.y_origin = stream.read_double('y origin')
            self.xy_scale = stream.read_double('xy scale')
            self.z_origin = stream.read_double('z origin')
            self.z_scale = stream.read_double('z scale')
            self.m_origin = stream.read_double('m origin')
            self.m_scale = stream.read_double('m scale')

        if version > 4:
            self.xy_tolerance = stream.read_double('xy tolerance')
            self.z_tolerance = stream.read_double('z tolerance')
            self.m_tolerance = stream.read_double('m tolerance')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'wkt': self.wkt,
            'x_origin': self.x_origin,
            'y_origin': self.y_origin,
            'xy_scale': self.xy_scale,
            'z_origin': None if math.isnan(self.z_origin) else self.z_origin,
            'z_scale': None if math.isnan(self.z_scale) else self.z_scale,
            'm_origin': None if math.isnan(self.m_origin) else self.m_origin,
            'm_scale': None if math.isnan(self.m_scale) else self.m_scale,
            'xy_tolerance': self.xy_tolerance,
            'z_tolerance': self.z_tolerance,
            'm_tolerance': self.m_tolerance,
            'is_high_precision': self.is_high_precision
        }

    @classmethod
    def from_dict(cls, definition: dict) -> 'GeographicCoordinateSystem':
        res = GeographicCoordinateSystem()
        res.wkt = definition['wkt']
        res.x_origin = definition['x_origin']
        res.y_origin = definition['y_origin']
        res.xy_scale = definition['xy_scale']
        res.z_origin = definition['z_origin']
        res.z_scale = definition['z_scale']
        res.m_origin = definition['m_origin']
        res.m_scale = definition['m_scale']
        res.xy_tolerance = definition['xy_tolerance']
        res.z_tolerance = definition['z_tolerance']
        res.m_tolerance = definition['m_tolerance']
        res.is_high_precision = definition['is_high_precision']
        return res
