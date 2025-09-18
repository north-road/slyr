#!/usr/bin/env python
"""
Serializable object subclass

NEAR COMPLETE INTERPRETATION - all useful components
"""

from .element import Element
from ..stream import Stream


class FrameElement(Element):
    """
    FrameElement
    """

    @staticmethod
    def cls_id():
        return "e01ba2c5-24b2-11d3-b8aa-00600802e603"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    @staticmethod
    def compatible_versions():
        return [2]

    def read(self, stream: Stream, version):
        stream.read_ushort("internal version", expected=3)
        self.shape = stream.read_object("shape")

        self.locked = stream.read_int("locked") != 0

        self.preserve_aspect = stream.read_ushort("fixed aspect ratio") != 0

        internal_version = stream.read_ushort("internal version", expected=(5, 6))

        self.element_name = stream.read_string("element name")
        self.element_type = stream.read_string("element type")

        variant_type = stream.read_ushort("custom property type")
        if variant_type:
            self.custom_property = stream.read_variant(variant_type, "custom property")

        self.auto_transform = stream.read_ushort("auto transform") != 0
        self.reference_scale = stream.read_double("reference scale")
        if internal_version > 5:
            self.anchor = stream.read_int("anchor")

        self.border = stream.read_object("border")
        self.background = stream.read_object("background")
        self.draft_mode = stream.read_ushort("draft mode") != 0
        self.shadow = stream.read_object("shadow")

    def to_dict(self):  # pylint: disable=method-hidden
        res = super().to_dict()
        return res
