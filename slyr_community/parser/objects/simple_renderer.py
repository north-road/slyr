#!/usr/bin/env python
"""
Simple Renderer

PARTIAL INTERPRETATION - all content from GUI is understood, but some unknown content
"""

from .vector_renderer import VectorRendererBase
from ..stream import Stream


class SimpleRenderer(VectorRendererBase):
    """
    Simple Renderer
    """

    @staticmethod
    def cls_id():
        return 'f3435801-5779-11d0-98bf-00805f7ced21'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.symbol = None
        self.legend_group = None

    @staticmethod
    def compatible_versions():
        return [1, 2, 3]

    def read(self, stream: Stream, version):
        self.symbol = stream.read_object('symbol')
        self.legend_group = stream.read_object('legend_group')
        # legend symbols are graduated?

        stream.read_ushort('unknown', expected=0)
        stream.read_double('unknown', expected=0)
        stream.read_double('unknown', expected=0)

        self.rotation_attribute = stream.read_string('rotation attribute')
        self.rotation_type = stream.read_int('rotation type')
        self.transparency_attribute = stream.read_string('transparency attribute')
        if version > 2:
            self.read_irotation_renderer2_properties(stream)
            self.read_graduated_size_properties(stream)

    def to_dict(self):  # pylint: disable=method-hidden
        res = super().to_dict()
        res['symbol'] = self.symbol.to_dict() if self.symbol else None
        res['legend_group'] = self.legend_group.to_dict() if self.legend_group else None
        return res
