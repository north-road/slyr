#!/usr/bin/env python
"""
Serializable object subclass
"""

from .element import Element
from ..stream import Stream


class RectangleElement(Element):
    """
    RectangleElement
    """

    @staticmethod
    def cls_id():
        return "3a9767c2-f253-11d0-83a4-080009b996cc"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    def read(self, stream: Stream, version):
        internal_version = stream.read_ushort("internal version", expected=(2, 3))

        self.shape = stream.read_object("polygon")
        self.locked = stream.read_int("locked") != 0

        if internal_version == 2:
            internal_version1 = stream.read_ushort(
                "internal version 1", expected=(3, 4)
            )
            self.element_name = stream.read_string("name")
            self.element_type = stream.read_string("type", expected="Rectangle")
            if internal_version1 == 3:
                stream.read_int("unknown", expected=0)
                stream.read_int("unknown", expected=0)
                stream.read_int("unknown", expected=0)
                stream.read_ushort("unknown", expected=0)

            stream.read_ushort("unknown", expected=0)
            stream.read_ushort("unknown", expected=65535)

        else:
            self.preserve_aspect = stream.read_ushort("preserve aspect ratio") != 0

            element_version = stream.read_ushort("element version", expected=(5, 6))

            self.element_name = stream.read_string("element name")
            self.element_type = stream.read_string("type")

            variant_type = stream.read_ushort("custom property type")
            if variant_type:
                self.custom_property = stream.read_variant(
                    variant_type, "custom property"
                )

            self.auto_transform = stream.read_ushort("auto transform") != 0
            self.reference_scale = stream.read_double("reference scale")

            if element_version > 5:
                self.anchor = stream.read_int("anchor")

        self.symbol = stream.read_object("symbol")

    def to_dict(self):  # pylint: disable=method-hidden
        res = super().to_dict()
        return res
