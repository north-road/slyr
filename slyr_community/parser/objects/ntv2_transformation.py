#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class NTv2Transformation(Object):
    """
    NTv2Transformation
    """

    @staticmethod
    def cls_id():
        return "52b971e2-ebec-11d4-9fd6-00c04f6bdd7f"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.wkt = ""

    def read(self, stream: Stream, version):
        self.wkt = stream.read_ascii("wkt")

    def to_dict(self):  # pylint: disable=method-hidden
        return {"wkt": self.wkt}
