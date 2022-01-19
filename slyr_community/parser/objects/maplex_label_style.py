#!/usr/bin/env python
"""
Serializable object subclass

"""

from ..object import Object
from ..stream import Stream


class MaplexLabelStyle(Object):
    """
    MaplexLabelStyle
    """

    @staticmethod
    def cls_id():
        return '20664808-cba7-11da-9f3a-00c34f6b26a5'

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
