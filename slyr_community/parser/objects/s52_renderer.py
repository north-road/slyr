#!/usr/bin/env python
"""
S52 Renderer

"""

from .vector_renderer import VectorRendererBase
from ..stream import Stream


class S52Renderer(VectorRendererBase):
    """
    S52 Renderer
    """

    @staticmethod
    def cls_id():
        return "ea77a441-5f16-4bd1-897d-17242d6b896e"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.symbol = None

    @staticmethod
    def compatible_versions():
        return None

    def read(self, stream: Stream, version):
        stream.push_object_store()
        self.symbol = stream.read_object("some symbol")
        stream.pop_object_store()

    def to_dict(self):  # pylint: disable=method-hidden
        res = super().to_dict()
        res["symbol"] = self.symbol.to_dict() if self.symbol else None
        return res
