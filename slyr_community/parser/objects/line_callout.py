#!/usr/bin/env python
"""
LineCallout

PARTIAL INTERPRETATION -- some unknown content, may not be robust
"""

from ..object import Object
from ..stream import Stream


class LineCallout(Object):
    """
    LineCallout
    """

    STYLE_BASE = 0
    STYLE_MIDPOINT = 1
    STYLE_THREE_POINT = 2
    STYLE_FOUR_POINT = 3
    STYLE_UNDERLINE = 4
    STYLE_CUSTOM = 5
    STYLE_CIRCULAR_CW = 6
    STYLE_CIRCULAR_CCW = 7

    @staticmethod
    def cls_id():
        return 'c8d09ed3-4fbb-11d1-9a72-0080c7ec5c96'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.border_symbol = None
        self.accent_symbol = None
        self.leader_symbol = None
        self.gap = 0.0
        self.style = LineCallout.STYLE_BASE
        self.margin_left = 0.0
        self.margin_top = 0.0
        self.margin_right = 0.0
        self.margin_bottom = 0.0
        self.tolerance = 0.0
        self.point = None

    @staticmethod
    def style_to_string(style):  # pylint: disable=too-many-return-statements
        """
        Converts style enum to string
        """
        if style == LineCallout.STYLE_BASE:
            return 'base'
        elif style == LineCallout.STYLE_MIDPOINT:
            return 'midpoint'
        elif style == LineCallout.STYLE_THREE_POINT:
            return 'three_point'
        elif style == LineCallout.STYLE_FOUR_POINT:
            return 'four_point'
        elif style == LineCallout.STYLE_UNDERLINE:
            return 'underline'
        elif style == LineCallout.STYLE_CUSTOM:
            return 'custom'
        elif style == LineCallout.STYLE_CIRCULAR_CW:
            return 'circular_cw'
        elif style == LineCallout.STYLE_CIRCULAR_CCW:
            return 'circular_ccw'
        return None

    def read(self, stream: Stream, version):
        self.border_symbol = stream.read_object('border symbol')
        self.accent_symbol = stream.read_object('accent symbol')
        self.leader_symbol = stream.read_object('leader symbol')

        self.point = stream.read_object('point')

        self.gap = stream.read_double('gap')
        self.style = stream.read_int('style')
        self.margin_left = stream.read_double('margin left')
        self.margin_top = stream.read_double('margin top')
        self.margin_right = stream.read_double('margin right')
        self.margin_bottom = stream.read_double('margin bottom')
        self.tolerance = stream.read_double('tolerance')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'margin_top': self.margin_top,
            'margin_right': self.margin_right,
            'margin_bottom': self.margin_bottom,
            'margin_left': self.margin_left,
            'border_symbol': self.border_symbol.to_dict() if self.border_symbol else None,
            'accent_symbol': self.accent_symbol.to_dict() if self.accent_symbol else None,
            'leader_symbol': self.leader_symbol.to_dict() if self.leader_symbol else None,
            'tolerance': self.tolerance,
            'gap': self.gap,
            'style': LineCallout.style_to_string(self.style),
            'point': self.point.to_dict() if self.point else None,
        }
