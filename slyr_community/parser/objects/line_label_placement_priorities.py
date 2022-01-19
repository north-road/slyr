#!/usr/bin/env python
"""
Serializable object subclass

NEAR COMPLETE INTERPRETATION -- some unknown content not exposed through GUI
"""

from ..object import Object
from ..stream import Stream


class LineLabelPlacementPriorities(Object):
    """
    LineLabelPlacementPriorities
    """

    @staticmethod
    def cls_id():
        return '261a4377-d9d5-11d2-a806-cc9f870bcd5a'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.above_before = 0
        self.above_at = 0
        self.above_after = 0
        self.on_line_before = 0
        self.on_line_at = 0
        self.on_line_after = 0
        self.below_before = 0
        self.below_at = 0
        self.below_after = 0

    def read(self, stream: Stream, version):
        stream.read_int('above start?')
        self.above_before = stream.read_int('above before')
        self.above_at = stream.read_int('above at')
        self.above_after = stream.read_int('above after')
        stream.read_int('above end?')
        stream.read_int('on line start?')
        self.on_line_before = stream.read_int('on line before')
        self.on_line_at = stream.read_int('on line at')
        self.on_line_after = stream.read_int('on line after')
        stream.read_int('on line end?')
        stream.read_int('below start?')
        self.below_before = stream.read_int('below before')
        self.below_at = stream.read_int('below at')
        self.below_after = stream.read_int('below after')
        stream.read_int('below end?')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'above_before': self.above_before,
            'above_at': self.above_at,
            'above_after': self.above_after,
            'on_line_before': self.on_line_before,
            'on_line_at': self.on_line_at,
            'on_line_after': self.on_line_after,
            'below_before': self.below_before,
            'below_at': self.below_at,
            'below_after': self.below_after,
        }
