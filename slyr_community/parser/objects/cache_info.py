#!/usr/bin/env python
"""
Serializable object subclass

COMPLETE INTERPRETATION
"""

from ...parser.object import Object
from ...parser.stream import Stream


class CacheInfo(Object):
    """
    CacheInfo
    """

    @staticmethod
    def cls_id():
        return "262e345e-b6cb-41cd-9f88-5453741e63f4"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.image_info = None
        self.tile_cache_info = None

    @staticmethod
    def compatible_versions():
        return None

    def read(self, stream: Stream, version):
        self.tile_cache_info = stream.read_object("tile cache info")
        self.image_info = stream.read_object("tile image info")

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "image_info": self.image_info.to_dict() if self.image_info else None,
            "tile_cache_info": self.tile_cache_info.to_dict()
            if self.tile_cache_info
            else None,
        }
