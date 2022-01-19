#!/usr/bin/env python
"""
SimpleLineCallout

PARTIAL INTERPRETATION - robust, but some unknown properties

"""

from ..object import Object
from ..stream import Stream


class SimpleLineCallout(Object):
    """
    SimpleLineCallout
    """

    @staticmethod
    def cls_id():
        return 'fa37b822-a959-4acd-834a-0e114bf420b8'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.tolerance = 0.0
        self.line_symbol = None
        self.auto_snap = True
        self.line = None
        self.point = None

    def read(self, stream: Stream, version):
        self.tolerance = stream.read_double('tolerance')
        self.auto_snap = stream.read_ushort('auto snap') != 0
        self.line = stream.read_object('line')
        self.line_symbol = stream.read_object('line symbol')
        self.point = stream.read_object('point')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'tolerance': self.tolerance,
            'auto_snap': self.auto_snap,
            'line_symbol': self.line_symbol.to_dict() if self.line_symbol else None,
            'line': self.line.to_dict() if self.line else None,
            'point': self.point.to_dict() if self.point else None
        }
