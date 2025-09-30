#!/usr/bin/env python
"""
Serializable object subclass
"""

from .element import Element
from ..stream import Stream


class TableFrame(Element):
    """
    TableFrame
    """

    @staticmethod
    def cls_id():
        return "316b169a-91e2-4131-98c2-b2c6ee955f0f"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.table_property = None
        self.table = None
        self.start_row = 0
        self.start_col = 0
        self.fields = None

    @staticmethod
    def compatible_versions():
        return [3, 4]

    def read(self, stream: Stream, version):
        stream.read_ushort("unknown", expected=2)
        stream.read_ushort("unknown", expected=3)

        self.shape = stream.read_object("shape")

        self.locked = stream.read_int("locked") != 0
        self.preserve_aspect = stream.read_ushort("fixed aspect ratio") != 0

        stream.read_ushort("internal version", expected=6)

        self.element_name = stream.read_string("element name")
        self.element_type = stream.read_string("element type", expected="Table")

        variant_type = stream.read_ushort("custom property type")
        if variant_type:
            self.custom_property = stream.read_variant(variant_type, "custom property")

        self.auto_transform = stream.read_ushort("auto transform") != 0
        self.reference_scale = stream.read_double("reference scale")
        self.anchor = stream.read_int("anchor")

        self.border = stream.read_object("border")
        self.background = stream.read_object("background")
        self.draft_mode = stream.read_ushort("draft mode") != 0
        self.shadow = stream.read_object("shadow")

        self.table_property = stream.read_object("table property")

        stream.read_ushort("unknown", expected=0)

        self.table = stream.read_object("table")

        stream.read_ushort("unknown", expected=65535)

        self.start_row = stream.read_int("start row")
        self.start_col = stream.read_int("start col")

        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)

        stream.read_object("picture")

        self.fields = stream.read_object("fields")

        if version > 3:
            stream.read_int("unknown", expected=0)
            stream.read_int("unknown", expected=0)
            stream.read_int("unknown", expected=0)
            stream.read_int("unknown", expected=0)

    def to_dict(self):  # pylint: disable=method-hidden
        res = super().to_dict()
        res["table_property"] = (
            self.table_property.to_dict() if self.table_property else None
        )
        res["table"] = self.table
        res["start_row"] = self.start_row
        res["start_col"] = self.start_col
        res["fields"] = self.fields.to_dict() if self.fields else None

        return res
