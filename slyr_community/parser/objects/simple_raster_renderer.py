#!/usr/bin/env python
"""
Serializable object subclass
"""

from .raster_renderer import RasterRenderer
from ..stream import Stream


class SimpleRasterRenderer(RasterRenderer):
    """
    SimpleRasterRenderer
    """

    @staticmethod
    def cls_id():
        return '3232d0ef-3460-4879-a1e6-366590cf3eec'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    @staticmethod
    def compatible_versions():
        return [2]

    def read(self, stream: Stream, version):
        stream.read_int('unknown', expected=0)
        super().read(stream, version)

    def to_dict(self):  # pylint: disable=method-hidden
        return {
        }
