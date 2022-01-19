#!/usr/bin/env python
"""
AnnotationExpressionParser

COMPLETE INTERPRETATION
"""

from ..object import Object
from ..stream import Stream


class DisplayExpressionProperties(Object):
    """
    DisplayExpressionProperties
    """

    @staticmethod
    def cls_id():
        return 'd75c6301-c05a-484c-a7bd-ae82e5e1fc75'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.expression = ''
        self.expression_parser = None
        self.advanced = False

    def read(self, stream: Stream, version):
        self.expression = stream.read_string('expression')
        self.advanced = stream.read_ushort('advanced') == 0
        self.expression_parser = stream.read_object('expression parser')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'expression': self.expression,
            'advanced': self.advanced,
            'expression_parser': self.expression_parser.to_dict() if self.expression_parser else None
        }
