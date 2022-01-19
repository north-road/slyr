#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream
from .geometry import Geometry
from ..object_registry import REGISTRY


class GeometryDef(Object):
    """
    GeometryDef
    """

    @staticmethod
    def cls_id():
        return '439a0d52-3915-11d1-9ca7-0000f8780619'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.geometry_type = Geometry.GEOMETRY_ANY
        self.average_number_of_points = 0
        self.spatial_index_grid_sizes = []
        self.crs = None
        self.has_m = False
        self.has_z = False

    def read(self, stream: Stream, version):
        self.average_number_of_points = stream.read_int('average number of points')

        count = stream.read_int('spatial index grid count')
        for i in range(count):
            self.spatial_index_grid_sizes.append(stream.read_double('spatial index grid size {}'.format(i + 1)))

        self.geometry_type = stream.read_int('geometry type')
        self.crs = stream.read_object('crs')

        self.has_z = stream.read_ushort('has z') != 0
        self.has_m = stream.read_ushort('has m') != 0

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'average_number_of_points': self.average_number_of_points,
            'geometry_type': Geometry.geometry_type_to_string(self.geometry_type),
            'crs': self.crs.to_dict() if self.crs else None,
            'has_m': self.has_m,
            'has_z': self.has_z
        }

    @classmethod
    def from_dict(cls, definition: dict) -> 'GeometryDef':
        res = GeometryDef()
        res.average_number_of_points = definition['average_number_of_points']
        res.geometry_type = Geometry.string_to_geometry_type(definition['geometry_type'])
        res.crs = REGISTRY.create_object_from_dict(definition['crs'])
        res.has_m = definition['has_m']
        res.has_z = definition['has_z']
        return res