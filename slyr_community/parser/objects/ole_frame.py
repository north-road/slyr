#!/usr/bin/env python
"""
Serializable object subclass
"""

from .element import Element
from ..stream import Stream


class OleFrame(Element):
    """
    OleFrame
    """

    @staticmethod
    def cls_id():
        return "f6705e85-523b-11d1-86e7-0000f8751720"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    def read(self, stream: Stream, version):
        stream.read_ushort("unknown", expected=1)
        stream.read_uchar("unknown", expected=0)
        stream.read_ushort("unknown", expected=1)
        stream.read_uchar("unknown", expected=0)

        stream.read_int("ole object id??")  # , expected=(1, 4, 23, 33))

        stream.read_int("unknown", expected=1)
        stream.read_ushort("unknown", expected=0)
        stream.read_int("unknown", expected=1)
        stream.read_ushort("unknown", expected=2)
        stream.read_ushort("unknown", expected=3)

        self.shape = stream.read_object("shape")

        stream.read_int("unknown", expected=0)

        self.draft_mode = stream.read_ushort("draft mode") != 0

        internal_version = stream.read_ushort("internal version", expected=(5, 6))

        self.element_name = stream.read_string("element name")
        self.element_type = stream.read_string("element type")

        stream.read_ushort("unknown", expected=0)
        stream.read_ushort("unknown flag", expected=65535)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)

        if internal_version > 5:
            self.anchor = stream.read_int("anchor")

        self.border = stream.read_object("border")
        self.background = stream.read_object("background")

        stream.read_ushort("maybe preserve aspect??", expected=(0, 65535))
        self.shadow = stream.read_object("shadow")

    def to_dict(self):  # pylint: disable=method-hidden
        res = super().to_dict()

        return res
