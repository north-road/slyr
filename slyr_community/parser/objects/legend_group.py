#!/usr/bin/env python
"""
LegendGroup

Contains an array of LegendClass

PARTIAL INTERPRETATION - robust, but some objects of unknown purpose.
"""

from ..object import Object
from ..stream import Stream


class LegendGroup(Object):
    """
    LegendGroup
    """

    @staticmethod
    def cls_id():
        return "167c5ea2-af20-11d1-8817-080009ec732a"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.classes = []
        self.heading = None
        self.visible = False
        self.editable_or_expanded = False

    @staticmethod
    def compatible_versions():
        return [2, 3]

    def read(self, stream: Stream, version):
        # visible? editable? symbols are graduated? -- may come first, as flags
        self.visible = stream.read_ushort("visible") != 0

        # expanded in some cases??
        self.editable_or_expanded = stream.read_ushort("editable or expanded") != 0
        self.heading = stream.read_string("heading")

        classes = stream.read_uint("class count")
        for _ in range(classes):
            self.classes.append(stream.read_object("class"))

        if version > 2:
            stream.read_ushort("unknown", expected=(0, 65535))

    def children(self):
        res = super().children()
        res.extend(self.classes)
        return res

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "heading": self.heading,
            "visible": self.visible,
            "editable_or_expanded": self.editable_or_expanded,
            "classes": [c.to_dict() for c in self.classes],
        }
