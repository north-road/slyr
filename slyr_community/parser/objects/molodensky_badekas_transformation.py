#!/usr/bin/env python
"""
Serializable object subclass

COMPLETE INTERPRETATION
"""

from ..object import Object
from ..stream import Stream


class MolodenskyBadekasTransformation(Object):
    """
    MolodenskyBadekasTransformation
    """

    @staticmethod
    def cls_id():
        return "e739e629-0d22-48f7-841c-54111ca6d666"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.wkt = ""

    def read(self, stream: Stream, version):
        self.wkt = stream.read_ascii("wkt")

    def to_dict(self):  # pylint: disable=method-hidden
        return {"wkt": self.wkt}
