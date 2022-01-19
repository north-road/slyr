#!/usr/bin/env python
"""
Serializable object subclass
"""

from .symbol_layer import SymbolLayer
from ..stream import Stream


class PieChartSymbol(SymbolLayer):
    """
    PieChartSymbol
    """

    @staticmethod
    def cls_id():
        return '50317368-bd70-11d3-9f79-00c04f6bc709'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.display_in_3d = False
        self.thinness = 0
        self.tilt_angle = 45
        self.starting_angle = 0
        self.clockwise = False
        self.outline = None
        self.symbols = []
        self.callout = None
        self.size = 0
        self.max_value = 0
        self.x_offset = 0
        self.y_offset = 0
        self.use_outline = True
        self.values = []

    def read(self, stream: Stream, version):
        self.size = stream.read_double('size related')
        self.starting_angle = stream.read_double('starting angle')

        self.x_offset = stream.read_double('x offset')
        self.y_offset = stream.read_double('y offset')

        self.display_in_3d = stream.read_uchar('display in 3d') != 0
        self.thinness = stream.read_double('thiness')
        self.tilt_angle = stream.read_int('tilt angle')
        self.clockwise = stream.read_ushort('clockwise') != 0
        self.outline = stream.read_object('outline')

        self.use_outline = stream.read_ushort('use outline') == 2
        stream.read_int('raster op code')
        stream.read_int('unknown', expected=0)
        self.max_value = stream.read_double('max value')

        count = stream.read_int('count')
        for i in range(count):
            self.symbols.append(stream.read_object('fill symbol {}'.format(i + 1)))
            self.values.append(stream.read_double('value {}'.format(i + 1)))

        self.callout = stream.read_object('line callout')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'display_in_3d': self.display_in_3d,
            'thinness': self.thinness,
            'tilt_angle': self.tilt_angle,
            'starting_angle': self.starting_angle,
            'clockwise': self.clockwise,
            'outline': self.outline.to_dict() if self.outline else None,
            'symbols': [s.to_dict() for s in self.symbols],
            'callout': self.callout.to_dict() if self.callout else None,
            'size': self.size,
            'max_value': self.max_value,
            'x_offset': self.x_offset,
            'y_offset': self.y_offset,
            'use_outline': self.use_outline,
            'values': self.values
        }
