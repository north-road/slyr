#!/usr/bin/env python
"""
Serializable object subclass

NEAR COMPLETE INTERPRETATION -- some unknown content not exposed through GUI
"""

from ..object import Object
from ..stream import Stream


class LineLabelPosition(Object):
    """
    LineLabelPosition
    """

    @staticmethod
    def cls_id():
        return '2442958c-d711-11d2-9f41-00c04f6bc6a5'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.above = False
        self.below = False
        self.online = False
        self.follow_line_orientation = False
        self.curved = False
        self.parallel = False
        self.perpendicular = False
        self.horizontal = False
        self.at_start = False
        self.at_end = False
        self.before_after_distance = 0.0
        self.best_position_along_line = False
        self.right_of_line = False

    @staticmethod
    def compatible_versions():
        return [2]

    def read(self, stream: Stream, version):
        self.above = stream.read_ushort('above') != 0
        self.below = stream.read_ushort('below') != 0
        self.online = stream.read_ushort('on line') != 0
        self.follow_line_orientation = stream.read_ushort('orientation line') != 0
        self.right_of_line = stream.read_ushort('right of line') != 0
        self.best_position_along_line = stream.read_ushort('best position along line') != 0
        self.at_start = stream.read_ushort('at start') != 0
        self.at_end = stream.read_ushort('at end') != 0
        self.parallel = stream.read_ushort('parallel') != 0
        self.perpendicular = stream.read_ushort('perpendicular') != 0
        self.horizontal = stream.read_ushort('horizontal') != 0
        self.before_after_distance = stream.read_double('before/after distance')
        # unsure what the difference here is vs curved
        self.curved = stream.read_ushort('curved labels') != 0

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'above': self.above,
            'below': self.below,
            'online': self.online,
            'follow_line_orientation': self.follow_line_orientation,
            'curved': self.curved,
            'parallel': self.parallel,
            'perpendicular': self.perpendicular,
            'horizontal': self.horizontal,
            'at_start': self.at_start,
            'at_end': self.at_end,
            'before_after_distance': self.before_after_distance,
            'best_position_along_line': self.best_position_along_line,
            'right_of_line': self.right_of_line
        }
