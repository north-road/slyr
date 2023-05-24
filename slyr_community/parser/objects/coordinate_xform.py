#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class CoordinateXForm(Object):
    """
    CoordinateXForm
    """

    @staticmethod
    def cls_id():
        return 'a11af4ab-9861-4e86-ac25-775668372108'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.input_crs = None
        self.crs = None
        self.tolerance = 0
        self.grid_size = 0
        self.recalculate_tolerance = True
        self.approximation = True

    def read(self, stream: Stream, version):
        stream.read_ushort('unknown', expected=0)

        self.input_crs = stream.read_object('input crs')
        self.crs = stream.read_object('crs')

        stream.read_double('unknown', expected=0)
        stream.read_double('unknown', expected=0)

        self.tolerance = stream.read_double('tolerance')
        self.grid_size = stream.read_int('grid size')
        self.recalculate_tolerance = stream.read_ushort('recalculate tolerance') == 65535
        self.approximation = stream.read_ushort('approximation') == 65535

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'input_crs': self.input_crs.to_dict() if self.input_crs else None,
            'crs': self.crs.to_dict() if self.crs else None,
            'tolerance': self.tolerance,
            'grid_size': self.grid_size,
            'recalculate_tolerance': self.recalculate_tolerance,
            'approximation': self.approximation,
        }
