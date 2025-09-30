#!/usr/bin/env python
"""
Serializable object subclass
"""

from .element import Element
from ..stream import Stream


class ParagraphTextElement(Element):
    """
    ParagraphTextElement
    """

    @staticmethod
    def cls_id():
        return "c84598b1-c4be-4203-9132-ada2be57f30c"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.column_gap = 0
        self.columns = 1
        self.margin = 0
        self.text = ""
        self.text_symbol = None
        self.scale_text = False

    def read(self, stream: Stream, version):
        self.border = stream.read_object("border")
        self.background = stream.read_object("background")
        self.shadow = stream.read_object("shadow")

        self.column_gap = stream.read_double("column gap")
        self.columns = stream.read_int("columns")
        self.margin = stream.read_double("margin")

        stream.read_ushort("unknown", expected=8)
        internal_version = stream.read_ushort("internal version?", expected=(5, 6))

        self.element_name = stream.read_string("element name")
        self.element_type = stream.read_string("type")

        variant_type = stream.read_ushort("custom property type")
        if variant_type:
            self.custom_property = stream.read_variant(variant_type, "custom property")
        self.auto_transform = stream.read_ushort("auto transform") != 0
        self.reference_scale = stream.read_double("reference scale")
        if internal_version > 5:
            self.anchor = stream.read_int("anchor")

        self.text = stream.read_string("text")

        self.scale_text = stream.read_int("scale text", expected=(0, 1)) != 0

        self.text_symbol = stream.read_object("text symbol")
        self.shape = stream.read_object("shape")

        self.locked = stream.read_int("locked") != 0
        stream.read_ushort("unknown", expected=65535)
        stream.read_ushort("unknown", expected=65535)

    def to_dict(self):  # pylint: disable=method-hidden
        res = super().to_dict()
        res["column_gap"] = self.column_gap
        res["columns"] = self.columns
        res["margin"] = self.margin
        res["text"] = self.text
        res["scale_text"] = self.scale_text
        res["text_symbol"] = self.text_symbol.to_dict() if self.text_symbol else None
        return res
