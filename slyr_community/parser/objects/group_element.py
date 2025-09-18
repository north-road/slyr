#!/usr/bin/env python
"""
Serializable object subclass
"""

from .element import Element
from ..stream import Stream


class GroupElement(Element):
    """
    GroupElement
    """

    @staticmethod
    def cls_id():
        return "803577d2-f8a3-11d0-83af-080009b996cc"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.elements = []

    @staticmethod
    def compatible_versions():
        return [2, 3]

    def read(self, stream: Stream, version):
        internal_version = stream.read_ushort("internal version?", expected=(4, 5, 6))

        self.element_name = stream.read_string("element name")
        self.element_type = stream.read_string("element type")

        variant_type = stream.read_ushort("custom property type")
        if variant_type:
            self.custom_property = stream.read_variant(variant_type, "custom property")

        self.auto_transform = stream.read_ushort("auto transform") != 0
        if internal_version > 4:
            self.reference_scale = stream.read_double("reference scale")

        if internal_version > 5:
            self.anchor = stream.read_int("anchor point")

        count = stream.read_int("count")
        for i in range(count):
            self.elements.append(stream.read_object("element {}".format(i + 1)))

        if version > 2:
            stream.read_object("shape")

        stream.read_ushort("unknown", expected=2)
        stream.read_ushort("unknown", expected=3)

        self.shape = stream.read_object("shape")

        self.locked = stream.read_int("locked") != 0
        self.preserve_aspect = stream.read_ushort("fixed aspect ratio") != 0

        if internal_version > 4:
            internal_version = stream.read_ushort("internal version 2", expected=(5, 6))

        stream.read_string("unknown")
        stream.read_string("type again", expected=self.element_type)

        variant_type = stream.read_ushort(
            "custom property type again", expected=variant_type
        )
        if variant_type:
            stream.read_variant(
                variant_type, "custom property again", expected=self.custom_property
            )
        stream.read_ushort(
            "auto transform again", expected=65535 if self.auto_transform else 0
        )

        if internal_version > 4:
            stream.read_double("reference scale again", expected=self.reference_scale)

        if internal_version > 5:
            stream.read_int("anchor point again", expected=self.anchor)

        self.border = stream.read_object("border")
        self.background = stream.read_object("background")
        self.draft_mode = stream.read_ushort("draft mode") != 0

        if internal_version > 4:
            self.shadow = stream.read_object("shadow")

        # was part of above..?

    #        if internal_version > 5:
    #            stream.read_ushort('unknown', expected=0)
    #            stream.read_ushort('unknown', expected=0)

    def to_dict(self):  # pylint: disable=method-hidden
        res = super().to_dict()
        res["elements"] = [e.to_dict() for e in self.elements]
        return res
