#!/usr/bin/env python
"""
Serializable object subclass
"""

from .element import Element
from ..stream import Stream


class MarkerElement(Element):
    """
    MarkerElement
    """

    @staticmethod
    def cls_id():
        return "530fd712-ef0c-11d0-83a0-080009b996cc"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0

    @staticmethod
    def compatible_versions():
        return [2, 3]

    def read(self, stream: Stream, version):
        internal_version = stream.read_ushort("internal version", expected=(3, 4, 5, 6))
        self.element_name = stream.read_string("element name")
        self.element_type = stream.read_string("type", expected="Marker")

        variant_type = stream.read_ushort("custom property type")
        if variant_type:
            self.custom_property = stream.read_variant(variant_type, "custom property")

        self.preserve_aspect = stream.read_ushort("preserve aspect ratio") != 0

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
        self.shape = stream.read_object("point")

        self.locked = stream.read_int("locked") != 0

        if version > 2:
            self.x = stream.read_double("x")
            self.y = stream.read_double("y")

            # x max/ymax
            self.width = stream.read_double("max x") - self.x
            self.height = stream.read_double("max y") - self.y

    def to_dict(self):  # pylint: disable=method-hidden
        res = super().to_dict()
        res["x"] = self.x
        res["y"] = self.y
        res["width"] = self.width
        res["height"] = self.height
        return res
