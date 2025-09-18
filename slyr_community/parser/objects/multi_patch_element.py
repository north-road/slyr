#!/usr/bin/env python
"""
Serializable object subclass
"""

from .element import Element
from ..stream import Stream


class MultiPatchElement(Element):
    """
    MultiPatchElement
    """

    @staticmethod
    def cls_id():
        return "e91ae5c9-2c16-11d4-80e2-00c04fa0adf8"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    @staticmethod
    def compatible_versions():
        return [1]

    def read(self, stream: Stream, version):
        internal_version = stream.read_ushort("internal version", expected=(5, 6))

        self.element_name = stream.read_string("element name")
        self.element_type = stream.read_string("name")

        variant_type = stream.read_ushort("custom property type")
        if variant_type:
            self.custom_property = stream.read_variant(variant_type, "custom property")

        self.auto_transform = stream.read_ushort("auto transform") != 0
        self.reference_scale = stream.read_double("reference scale")

        if internal_version > 5:
            self.anchor = stream.read_int("anchor")
        self.symbol = stream.read_object("symbol")
        self.shape = stream.read_object("line")

        self.locked = stream.read_int("locked") != 0

        self.preserve_aspect = stream.read_ushort("preserve aspect ratio") != 0

    def to_dict(self):  # pylint: disable=method-hidden
        res = super().to_dict()
        return res
