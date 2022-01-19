#!/usr/bin/env python
"""
Serializable object subclass

COMPLETE INTERPRETATION
"""

from ..object import Object
from ..stream import Stream


class LabelStyle(Object):
    """
    LabelStyle
    """

    @staticmethod
    def cls_id():
        return '4c90de7b-cb77-11d2-9f34-00c04f6bc6a5'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.text_symbol = None
        self.overposter = None

    def read(self, stream: Stream, version):
        self.text_symbol = stream.read_object('text symbol')
        self.overposter = stream.read_object('overposter')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'text_symbol': self.text_symbol.to_dict() if self.text_symbol else None,
            'overposter': self.overposter.to_dict() if self.overposter else None
        }
