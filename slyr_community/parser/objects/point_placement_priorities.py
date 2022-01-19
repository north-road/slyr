#!/usr/bin/env python
"""
Serializable object subclass

COMPLETE INTERPRETATION
"""

from ..object import Object
from ..stream import Stream


class PointPlacementPriorities(Object):
    """
    PointPlacementPriorities
    """

    @staticmethod
    def cls_id():
        return '261a4372-d9d5-11d2-a806-cc9f870bcd5a'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.top_left = 0
        self.top_center = 0
        self.top_right = 0
        self.center_right = 0
        self.bottom_right = 0
        self.bottom_center = 0
        self.bottom_left = 0
        self.center_left = 0

    def read(self, stream: Stream, version):
        self.top_left = stream.read_int('top left')
        self.top_center = stream.read_int('top center')
        self.top_right = stream.read_int('top right')
        self.center_right = stream.read_int('center right')
        self.bottom_right = stream.read_int('bottom_right')
        self.bottom_center = stream.read_int('bottom center')
        self.bottom_left = stream.read_int('bottom left')
        self.center_left = stream.read_int('center left')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'top_left': self.top_left,
            'top_center': self.top_center,
            'top_right': self.top_right,
            'center_right': self.center_right,
            'bottom_right': self.bottom_right,
            'bottom_center': self.bottom_center,
            'bottom_left': self.bottom_left,
            'center_left': self.center_left
        }
