#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class RasterDef(Object):
    """
    RasterDef
    """

    @staticmethod
    def cls_id():
        return 'a8386192-3659-4525-984f-5d643a40ee8c'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.description = ''
        self.crs = None
        self.is_raster_dataset = False
        self.is_function = False
        self.is_managed = False

    @staticmethod
    def compatible_versions():
        return [2, 3]

    def read(self, stream: Stream, version):
        self.description = stream.read_string('description')
        self.crs = stream.read_object('crs')

        self.is_raster_dataset = stream.read_ushort('is raster dataset') != 0
        self.is_managed = stream.read_ushort('is NOT managed') != 65535
        self.is_function = stream.read_ushort('is function') != 0

        if version > 2:
            stream.read_ushort('unknown', expected=0)

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'description': self.description,
            'crs': self.crs.to_dict() if self.crs else None,
            'is_raster_dataset': self.is_raster_dataset,
            'is_function': self.is_function,
            'is_managed': self.is_managed
        }
