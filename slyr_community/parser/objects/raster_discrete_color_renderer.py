#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..stream import Stream
from .raster_renderer import RasterRenderer


class RasterDiscreteColorRenderer(RasterRenderer):
    """
    RasterDiscreteColorRenderer
    """

    @staticmethod
    def cls_id():
        return 'ac874573-d778-4421-b9c6-14557d8bd692'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.ramp_name = ''
        self.number_of_colors = 0
        self.color_ramp = None

    def read(self, stream: Stream, version):
        stream.read_ushort('unknown', expected=0)

        self.number_of_colors = stream.read_int('number of colors')
        for i in range(self.number_of_colors):
            stream.read_int('unknown {}'.format(i + 1))

        self.ramp_name = stream.read_string('ramp name')
        self.color_ramp = stream.read_object('color ramp')

        super().read(stream, 2)

    def to_dict(self):  # pylint: disable=method-hidden
        res = super().to_dict()
        res['ramp_name'] = self.ramp_name
        res['number_of_colors'] = self.number_of_colors
        res['color_ramp'] = self.color_ramp.to_dict() if self.color_ramp else None
        return res
