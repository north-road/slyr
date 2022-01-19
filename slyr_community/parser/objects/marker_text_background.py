#!/usr/bin/env python
"""
MarkerTextBackground

COMPLETE INTERPRETATION

"""

from ..object import Object
from ..stream import Stream


class MarkerTextBackground(Object):
    """
    MarkerTextBackground
    """

    @staticmethod
    def cls_id():
        return 'c5c02d50-7282-11d2-9816-0080c7e04196'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.marker_symbol = None
        self.scale_to_fit_text = False

    def read(self, stream: Stream, version):
        self.scale_to_fit_text = stream.read_ushort('scale to fit text') != 0
        self.marker_symbol = stream.read_object('marker symbol')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'marker_symbol': self.marker_symbol.to_dict() if self.marker_symbol else None,
            'scale_to_fit_text': self.scale_to_fit_text
        }
