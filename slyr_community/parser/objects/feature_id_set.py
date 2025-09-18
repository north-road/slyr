#!/usr/bin/env python
"""
Serializable object subclass

COMPLETE INTERPRETATION
"""

from ..object import Object
from ..stream import Stream


class FeatureIDSet(Object):
    """
    FeatureIDSet
    """

    @staticmethod
    def cls_id():
        return "d5bb4b88-e0a1-11d2-9f4d-00c04f6bc78e"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.features = []

    def read(self, stream: Stream, version):
        count = stream.read_int("count")
        for i in range(count):
            self.features.append(stream.read_int("id {}".format(i + 1)))

    def to_dict(self):  # pylint: disable=method-hidden
        return {"features": self.features}
