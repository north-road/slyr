#!/usr/bin/env python
"""
Serializable object subclass

COMPLETE INTERPRETATION
"""

from ..object import Object
from ..stream import Stream


class AbridgedMolodenskyTransformation(Object):
    """
    AbridgedMolodenskyTransformation
    """

    @staticmethod
    def cls_id():
        return "dd2f68d0-c6b0-11d2-bd09-0000f875bcce"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.wkt = ""

    def read(self, stream: Stream, version):
        self.wkt = stream.read_ascii("wkt")

    def to_dict(self):  # pylint: disable=method-hidden
        return {"wkt": self.wkt}
