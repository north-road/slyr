#!/usr/bin/env python
"""
Serializable object subclass

PARTIAL IMPLEMENTATION - ALL USEFUL OBJECTS
"""

from ..object import Object
from ..stream import Stream


class ElementCollection(Object):
    """
    ElementCollection
    """

    @staticmethod
    def cls_id():
        return "ce8f3972-e9be-11d1-a232-080009b6f22b"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.elements = []
        self.linked_feature_ids = []

    def __repr__(self):
        if self.ref_id is not None:
            return "<ElementCollection: {} members ({})>".format(
                len(self.elements), self.ref_id
            )
        else:
            return "<ElementCollection: {} members>".format(len(self.elements))

    @staticmethod
    def compatible_versions():
        return [2, 4]

    def read(self, stream: Stream, version):
        count = stream.read_int("count")
        for i in range(count):
            self.elements.append(stream.read_object("element {}".format(i + 1)))
            if version > 2:
                self.linked_feature_ids.append(stream.read_int("linked feature id"))
                stream.read_ushort("unknown", expected=65535)
                stream.read_ushort("unknown", expected=65535)
                stream.read_int("unknown", expected=0)

        if version <= 2:
            for i in range(count):
                # looks kind of like a size?
                stream.read_int("unknown")

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "elements": [e.to_dict() for e in self.elements],
            "linked_feature_ids": self.linked_feature_ids,
        }
