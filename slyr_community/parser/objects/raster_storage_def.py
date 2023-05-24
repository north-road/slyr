#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class RasterStorageDef(Object):
    """
    RasterStorageDef
    """

    @staticmethod
    def cls_id():
        return '82abc602-67f9-4042-bee1-645b0139fd70'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.tile_width = 0
        self.tile_height = 0
        self.compression_quality = 0
        self.resampling_type = 0  # rstResamplingTypes
        self.pyramid_level = 0
        self.compression_type = 0  # esriRasterCompressionType
        self.cell_size_x = None
        self.cell_size_y = None
        self.origin = None
        self.tiled = False
        self.creation_options = ''

    @staticmethod
    def compatible_versions():
        return [4]

    def read(self, stream: Stream, version):
        self.tile_width = stream.read_int('tile width')
        self.tile_height = stream.read_int('tile height')
        self.compression_quality = stream.read_int('compression quality')
        self.resampling_type = stream.read_int('resampling type')
        self.pyramid_level = stream.read_int('pyramid level')
        self.compression_type = stream.read_int('compression type')

        if stream.read_uchar('has cell size'):
            self.cell_size_x = stream.read_double('cell size x')
            self.cell_size_y = stream.read_double('cell size y')
        self.origin = stream.read_object('origin')

        self.tiled = stream.read_ushort('tiled') != 0
        self.creation_options = stream.read_string('creation options')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'tile_width': self.tile_width,
            'tile_height': self.tile_height,
            'compression_quality': self.compression_quality,
            'resampling_type': self.resampling_type,
            'pyramid_level': self.pyramid_level,
            'compression_type': self.compression_type,
            'cell_size_x': self.cell_size_x,
            'cell_size_y': self.cell_size_y,
            'origin': self.origin.to_dict() if self.origin else None,
            'tiled': self.tiled,
            'creation_options': self.creation_options,
        }
