#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class AnnotateMap(Object):
    """
    AnnotateMap
    """

    @staticmethod
    def cls_id():
        return "8c439002-14ec-11d2-a27e-080009b6f22b"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    def read(self, stream: Stream, version):
        pass

    def to_dict(self):  # pylint: disable=method-hidden
        return {}
