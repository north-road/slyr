#!/usr/bin/env python
"""
Serializable object subclass

NEAR COMPLETE INTERPRETATION - all useful components
"""

from .element import Element
from ..stream import Stream


class EllipseElement(Element):
    """
    EllipseElement
    """

    @staticmethod
    def cls_id():
        return "4eda1081-12ea-11d3-9f8f-00c04f6bc8dd"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    def read(self, stream: Stream, version):
        stream.read_ushort("internal version", expected=3)

        self.shape = stream.read_object("polygon")
        self.locked = stream.read_int("locked") != 0
        self.preserve_aspect = stream.read_ushort("preserve aspect ratio") != 0

        internal_version = stream.read_ushort("internal version", expected=(5, 6))

        self.element_name = stream.read_string("element name")
        self.element_type = stream.read_string("name", expected="Ellipse")

        variant_type = stream.read_ushort("custom property type")
        if variant_type:
            self.custom_property = stream.read_variant(variant_type, "custom property")

        self.auto_transform = stream.read_ushort("auto transform") != 0
        self.reference_scale = stream.read_double("reference scale")
        if internal_version > 5:
            self.anchor = stream.read_int("anchor")
        self.symbol = stream.read_object("symbol")

    def to_dict(self):  # pylint: disable=method-hidden
        res = super().to_dict()
        return res
