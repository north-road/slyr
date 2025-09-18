#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class TimeInstant(Object):
    """
    TimeInstant
    """

    @staticmethod
    def cls_id():
        return "06bd7287-0785-4294-bd72-f2933b7fd00d"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.time = None
        self.reference = None

    def read(self, stream: Stream, version):
        self.time = stream.read_object("time")
        self.reference = stream.read_object("time reference")

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "time": self.time.to_dict() if self.time else None,
            "reference": self.reference.to_dict() if self.reference else None,
        }
