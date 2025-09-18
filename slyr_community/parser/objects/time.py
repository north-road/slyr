#!/usr/bin/env python
"""
Time

NEAR COMPLETE INTERPRETATION:
"""

from ..object import Object
from ..stream import Stream


class Time(Object):
    """
    Actually a datetime value
    """

    @staticmethod
    def cls_id():
        return "e1721810-8210-45b1-8590-fc4c911fba20"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.year = 0
        self.month = 0
        self.day = 0
        self.hour = 0
        self.minute = 0
        self.second = 0
        self.nanoseconds = 0

    def read(self, stream: Stream, version):
        stream.read_int("unknown", expected=2)
        self.year = stream.read_ushort("year")
        self.month = stream.read_ushort("month")
        self.day = stream.read_ushort("day")
        self.hour = stream.read_ushort("hour")
        self.minute = stream.read_ushort("minute")
        self.second = stream.read_ushort("second")
        self.nanoseconds = stream.read_int("nanoseconds")

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "year": self.year,
            "month": self.month,
            "day": self.day,
            "hour": self.hour,
            "minute": self.minute,
            "second": self.second,
            "nanoseconds": self.nanoseconds,
        }
