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
        return [6]

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    def read(self, stream: Stream, version):
        stream.read_int("unknown", expected=0)
        stream.read_string("unknown", expected="")
        stream.read_int("unknown", expected=4)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=1)
        stream.read_int("unknown", expected=0)
        stream.read_ushort("unknown", expected=0)
        stream.read_string("unknown", expected="New")

    def to_dict(self):  # pylint: disable=method-hidden
        return {}
