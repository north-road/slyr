#!/usr/bin/env python
"""
Serializable object subclass

COMPLETE INTERPRETATION
"""

from ..object import Object
from ..stream import Stream


class MapOptimizationLayoutExtension(Object):
    """
    MapOptimizationLayoutExtension
    """

    @staticmethod
    def cls_id():
        return "6c29d89f-b7ba-4fb0-a88d-fea77a03ba0e"

    @staticmethod
    def compatible_versions():
        return [1, 6]

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    def read(self, stream: Stream, version):
        count = stream.read_int("unknown count")
        for i in range(count):
            stream.read_ushort("unknown", expected=2)
            stream.read_int("unknown", expected=(10009, 24033, 30005))
            stream.read_int("unknown", expected=(1, 2))
            stream.read_object("converter option")
            object_count = stream.read_int("unknown object count {}".format(i + 1))
            for j in range(object_count):
                stream.read_object("linked object {}".format(j + 1))

        if version > 1:
            stream.read_string("unknown", expected="")
            stream.read_int("unknown", expected=4)
            stream.read_int("unknown", expected=0)
            stream.read_int("unknown", expected=0)
            stream.read_int("unknown", expected=0)

            stream.read_int("unknown", expected=(0, 4))
            stream.read_int("unknown", expected=0)
            stream.read_int("unknown", expected=(0, 1))
            stream.read_int("unknown", expected=0)
            stream.read_ushort("ushort", expected=0)
            stream.read_string("unknown", expected="New")

    def to_dict(self):  # pylint: disable=method-hidden
        return {}
