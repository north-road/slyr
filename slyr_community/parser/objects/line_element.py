#!/usr/bin/env python
"""
Serializable object subclass
"""

from .element import Element
from ..stream import Stream


class LineElement(Element):
    """
    LineElement
    """

    @staticmethod
    def cls_id():
        return "8ab7fbe1-d871-11d0-8389-080009b996cc"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    @staticmethod
    def compatible_versions():
        return [2, 3]

    def read(self, stream: Stream, version):
        internal_version = stream.read_ushort("internal version", expected=(3, 4, 5, 6))

        self.element_name = stream.read_string("element name")
        self.element_type = stream.read_string("type", expected=("Line", "Linie"))

        variant_type = stream.read_ushort("custom property type")
        if variant_type:
            self.custom_property = stream.read_variant(variant_type, "custom property")

        self.auto_transform = stream.read_ushort("auto transform") != 0

        if internal_version == 3:
            stream.read_int("unknown", expected=0)
            stream.read_int("unknown", expected=0)
            stream.read_int("unknown", expected=0)
            stream.read_ushort("unknown", expected=65535)

        if internal_version > 4:
            self.reference_scale = stream.read_double("reference scale")

        if internal_version > 5:
            self.anchor = stream.read_int("anchor")
        self.symbol = stream.read_object("symbol")
        self.shape = stream.read_object("line")

        self.locked = stream.read_int("locked") != 0

        if internal_version > 4:
            self.preserve_aspect = stream.read_ushort("preserve aspect ratio") != 0

    def to_dict(self):  # pylint: disable=method-hidden
        res = super().to_dict()
        return res
