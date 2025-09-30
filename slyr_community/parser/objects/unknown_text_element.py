#!/usr/bin/env python
"""
Serializable object subclass
"""

from .element import Element
from ..stream import Stream


class UnknownTextElement(Element):
    """
    UnknownTextElement??
    """

    @staticmethod
    def cls_id():
        return "885e7de2-ac2d-4942-b20d-9e95fab811b0"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.text_symbol = None
        self.text = ""
        self.annotation_group_index = 0

    @staticmethod
    def compatible_versions():
        return None

    def read(self, stream: Stream, version):
        # self.element_name = stream.read_stringv2('element name')
        # self.element_type = stream.read_string('element type')

        # variant_type = stream.read_ushort('custom property type')
        # if variant_type:
        #    self.custom_property = stream.read_variant(variant_type, 'custom property')
        stream.read_ushort("custom property type", expected=8)
        stream.read_stringv2("custom property", expected="1.0")

        stream.read_ushort("unknown", expected=13)

        self.shape = stream.read_object("shape")

        stream.read_ushort("unknown", expected=13)

        self.text_symbol = stream.read_object("text symbol")

        stream.read_ushort("unknown", expected=8)
        stream.read_stringv2("unknown", expected="PathElement2")

        stream.read_ushort("unknown", expected=8)
        stream.read_stringv2("unknown", expected="PathElement")

        stream.read_ushort("unknown", expected=8)
        stream.read_stringv2("some file path to mxd")

        stream.read_ushort("unknown", expected=11)
        stream.read_ushort("unknown", expected=0)

        stream.read_ushort("unknown", expected=0)

        stream.read_ushort("unknown", expected=11)
        stream.read_ushort("unknown", expected=0)

        stream.read_ushort("unknown", expected=7)
        stream.read_int("unknown", expected=0)

        stream.read_ushort("unknown", expected=30688)
        stream.read_ushort("unknown", expected=16611)

        stream.read_ushort("unknown", expected=8)
        stream.read_stringv2("some time?")

        stream.read_ushort("unknown", expected=11)
        stream.read_ushort("unknown", expected=0)

        stream.read_ushort("unknown", expected=11)
        stream.read_ushort("unknown", expected=65535)

    def to_dict(self):  # pylint: disable=method-hidden
        res = super().to_dict()
        res["text"] = self.text
        res["text_symbol"] = self.text_symbol.to_dict() if self.text_symbol else None
        res["annotation_group_index"] = self.annotation_group_index
        return res
