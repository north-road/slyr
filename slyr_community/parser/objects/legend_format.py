#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class LegendFormat(Object):
    """
    LegendFormat
    """

    @staticmethod
    def cls_id():
        return "7a3f91e5-b9e3-11d1-8756-0000f8751720"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.show_title = True
        self.title_text_symbol = None
        self.title_gap = 0
        self.item_gap = 0
        self.column_gap = 0
        self.layer_name_gap = 0
        self.heading_gap = 0
        self.text_gap = 0
        self.vertical_patch_gap = 0
        self.patch_gap = 0
        self.group_gap = 0
        self.default_width = 30
        self.default_height = 15
        self.default_line_patch = None
        self.default_area_patch = None

    @staticmethod
    def compatible_versions():
        return [1, 2]

    def read(self, stream: Stream, version):
        self.show_title = stream.read_ushort("show title") != 0
        self.title_text_symbol = stream.read_object("text symbol")

        stream.read_int("unknown", expected=1)

        self.title_gap = stream.read_double("title gap")
        self.item_gap = stream.read_double("item gap")
        self.column_gap = stream.read_double("column gap")
        self.layer_name_gap = stream.read_double("layer name gap")
        self.group_gap = stream.read_double("group gap")
        self.heading_gap = stream.read_double("heading gap")
        self.text_gap = stream.read_double("text gap")
        self.vertical_patch_gap = stream.read_double("vertical patch gap")
        self.patch_gap = stream.read_double("patch gap")
        self.default_width = stream.read_double("default width")
        self.default_height = stream.read_double("default height")
        self.default_line_patch = stream.read_object("default line patch")
        self.default_area_patch = stream.read_object("default area patch")

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "show_title": self.show_title,
            "title_text_symbol": self.title_text_symbol.to_dict()
            if self.title_text_symbol
            else None,
            "title_gap": self.title_gap,
            "item_gap": self.item_gap,
            "column_gap": self.column_gap,
            "layer_name_gap": self.layer_name_gap,
            "heading_gap": self.heading_gap,
            "text_gap": self.text_gap,
            "vertical_patch_gap": self.vertical_patch_gap,
            "patch_gap": self.patch_gap,
            "group_gap": self.group_gap,
            "default_width": self.default_width,
            "default_height": self.default_height,
            "default_line_patch": self.default_line_patch.to_dict()
            if self.default_line_patch
            else None,
            "default_area_patch": self.default_area_patch.to_dict()
            if self.default_area_patch
            else None,
        }
