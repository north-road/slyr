#!/usr/bin/env python
"""
BalloonCallout

COMPLETE INTERPRETATION
"""

from ..object import Object
from ..stream import Stream


class BalloonCallout(Object):
    """
    BalloonCallout
    """

    STYLE_RECTANGLE = 0
    STYLE_ROUNDED_RECTANGLE = 1
    STYLE_OVAL = 2

    @staticmethod
    def cls_id():
        return 'c8d09ed2-4fbb-11d1-9a72-0080c7ec5c96'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.margin_top = 0.0
        self.margin_right = 0.0
        self.margin_bottom = 0.0
        self.margin_left = 0.0
        self.fill_symbol = None
        self.tolerance = 0.0
        self.point = None
        self.style = BalloonCallout.STYLE_RECTANGLE

    @staticmethod
    def style_to_string(style):
        """
        Converts style enum to a string
        """
        if style == BalloonCallout.STYLE_RECTANGLE:
            return 'rectangle'
        elif style == BalloonCallout.STYLE_OVAL:
            return 'oval'
        elif style == BalloonCallout.STYLE_ROUNDED_RECTANGLE:
            return 'rounded_rectangle'
        return None

    def read(self, stream: Stream, version):
        self.style = stream.read_int('style')
        self.margin_left = stream.read_double('margin left')
        self.margin_top = stream.read_double('margin top')
        self.margin_right = stream.read_double('margin right')
        self.margin_bottom = stream.read_double('margin bottom')
        self.fill_symbol = stream.read_object('fill symbol')
        self.point = stream.read_object('point')
        self.tolerance = stream.read_double('tolerance')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'margin_top': self.margin_top,
            'margin_right': self.margin_right,
            'margin_bottom': self.margin_bottom,
            'margin_left': self.margin_left,
            'fill_symbol': self.fill_symbol.to_dict() if self.fill_symbol else None,
            'tolerance': self.tolerance,
            'style': BalloonCallout.style_to_string(self.style),
            'point': self.point.to_dict() if self.point else None
        }
