#!/usr/bin/env python
"""
Serializable object subclass

COMPLETE INTERPRETATION
"""

from ..object import Object
from ..stream import Stream


class UID(Object):
    """
    UID
    """

    @staticmethod
    def cls_id():
        return "78ff7fa1-fb2f-11d1-94a2-080009eebecb"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.sub_type = 0
        self.value = None

    def read(self, stream: Stream, version):
        stream.read_uchar("has value set", expected=(0, 1))

        self.value = stream.read_raw_clsid("value")
        self.sub_type = stream.read_int("sub type")

    def to_dict(self):  # pylint: disable=method-hidden
        return {"value": self.value, "sub_type": self.sub_type}
