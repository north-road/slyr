#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class NADCONTransformation(Object):
    """
    NADCONTransformation
    """

    @staticmethod
    def cls_id():
        return "d661941c-da8a-11d3-9f60-00c04f6bdd7f"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.wkt = ""

    def read(self, stream: Stream, version):
        self.wkt = stream.read_ascii("wkt")

    def to_dict(self):  # pylint: disable=method-hidden
        return {"wkt": self.wkt}
