#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class RulerSettings(Object):
    """
    RulerSettings
    """

    @staticmethod
    def cls_id():
        return "31e081ac-cb02-11d1-876c-0000f8751720"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.smallest_division = 0

    def read(self, stream: Stream, version):
        self.smallest_division = stream.read_double("smallest div")

    def to_dict(self):  # pylint: disable=method-hidden
        return {"smallest_division": self.smallest_division}
