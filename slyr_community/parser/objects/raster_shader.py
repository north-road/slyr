#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class RasterShader(Object):
    """
    RasterShader
    """

    @staticmethod
    def cls_id():
        return "9a895dac-e565-488e-a5f4-8b395327e2be"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    @staticmethod
    def compatible_versions():
        return [1]

    def read(self, stream: Stream, version):
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        # not sure where this ends, check RasterBasemapLayer

    def to_dict(self):  # pylint: disable=method-hidden
        return {}
