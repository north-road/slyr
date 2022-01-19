#!/usr/bin/env python
"""
HotLinkExpressionProperties

COMPLETE INTERPRETATION
"""

from ..object import Object
from ..stream import Stream


class HotLinkExpressionProperties(Object):
    """
    Relates to hyperlinks
    """

    @staticmethod
    def cls_id():
        return '1b848b0f-5e87-4948-841a-86201facd925'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.expression = ''
        self.parser = None
        self.is_expression_simple = False

    def read(self, stream: Stream, version):
        self.expression = stream.read_string('expression')
        self.is_expression_simple = stream.read_ushort('is expression simple') != 0
        self.parser = stream.read_object('parser')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'expression': self.expression,
            'is_expression_simple': self.is_expression_simple,
            'parser': self.parser.to_dict() if self.parser else None
        }
