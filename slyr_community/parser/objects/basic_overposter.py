#!/usr/bin/env python
"""
Serializable object subclass

COMPLETE INTERPRETATION
"""

from ..object import Object
from ..stream import Stream


class BasicOverposter(Object):
    """
    BasicOverposter
    """

    @staticmethod
    def cls_id():
        return "3141f2fc-38e2-11d1-8809-080009ec732a"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.label_properties = []

    def read(self, stream: Stream, version):
        count = stream.read_int("count")
        for i in range(count):
            self.label_properties.append(
                stream.read_object("properties {}".format(i + 1))
            )

    def to_dict(self):  # pylint: disable=method-hidden
        return {"properties": [p.to_dict() for p in self.label_properties]}
