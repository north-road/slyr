#!/usr/bin/env python
"""
Serializable object subclass
"""

from .element import Element
from ..stream import Stream


class TextElement(Element):
    """
    TextElement
    """

    @staticmethod
    def cls_id():
        return "204034d3-f6ea-11d0-83ad-080009b996cc"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.text_symbol = None
        self.text = ""
        self.annotation_group_index = 0

    @staticmethod
    def compatible_versions():
        return [4, 6, 8]

    def read(self, stream: Stream, version):
        internal_version = stream.read_ushort(
            "internal version?", expected=(3, 4, 5, 6)
        )

        self.element_name = stream.read_string("element name")
        self.element_type = stream.read_string("element type")

        if internal_version > 3:
            variant_type = stream.read_ushort("custom property type")
            if variant_type:
                self.custom_property = stream.read_variant(
                    variant_type, "custom property"
                )
        else:
            stream.read_double("unknown", expected=0)
            stream.read_double("unknown", expected=0)

        self.auto_transform = stream.read_ushort("auto transform") != 0

        if internal_version > 4:
            self.reference_scale = stream.read_double("reference scale")

        if internal_version >= 6:
            self.anchor = stream.read_int("anchor")

        self.text = stream.read_string("label contents")

        # somewhere must be a flag to say not in group?
        self.annotation_group_index = stream.read_int("annotation group index")

        self.text_symbol = stream.read_object("text symbol")
        self.shape = stream.read_object("shape")

        self.locked = stream.read_int("locked") != 0
        stream.read_ushort("unknown flag", expected=65535)
        stream.read_ushort("unknown flag", expected=65535)

    def to_dict(self):  # pylint: disable=method-hidden
        res = super().to_dict()
        res["text"] = self.text
        res["text_symbol"] = self.text_symbol.to_dict() if self.text_symbol else None
        res["annotation_group_index"] = self.annotation_group_index
        return res
