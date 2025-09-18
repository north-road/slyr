#!/usr/bin/env python
"""
TimeExtent

PARTIAL INTERPRETATION:
"""

from ..object import Object
from ..stream import Stream


class TimeExtent(Object):
    """
    A time span/extent store
    """

    @staticmethod
    def cls_id():
        return "5dc783de-283a-4963-ab53-25a05c5d76cc"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.start = None
        self.end = None
        self.reference = None
        self.empty = False

    @staticmethod
    def compatible_versions():
        return [2]

    def read(self, stream: Stream, version):
        self.start = stream.read_object("start")
        self.end = stream.read_object("end")
        self.reference = stream.read_object("reference")
        self.empty = stream.read_uchar("empty?") == 0

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "start": self.start.to_dict() if self.start else None,
            "end": self.end.to_dict() if self.end else None,
            "reference": self.reference.to_dict() if self.reference else None,
            "empty": self.empty,
        }
