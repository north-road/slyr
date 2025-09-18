#!/usr/bin/env python
"""
Serializable object subclass

NEAR COMPLETE INTERPRETATION - all useful components
"""

from ..object import Object
from ..stream import Stream


class HorizontalBarLegendItem(Object):
    """
    HorizontalBarLegendItem
    """

    ARRANGEMENT_SYMBOL_LABEL_DESCRIPTION = 0
    ARRANGEMENT_SYMBOL_DESCRIPTION_LABEL = 1
    ARRANGEMENT_LABEL_SYMBOL_DESCRIPTION = 2
    ARRANGEMENT_LABEL_DESCRIPTION_SYMBOL = 3
    ARRANGEMENT_DESCRIPTION_SYMBOL_LABEL = 4
    ARRANGEMENT_DESCRIPTION_LABEL_SYMBOL = 5

    @staticmethod
    def arrangement_to_string(arrangement) -> str:
        if arrangement == HorizontalBarLegendItem.ARRANGEMENT_SYMBOL_LABEL_DESCRIPTION:
            return "symbol_label_description"
        elif (
            arrangement == HorizontalBarLegendItem.ARRANGEMENT_SYMBOL_DESCRIPTION_LABEL
        ):
            return "symbol_description_label"
        elif (
            arrangement == HorizontalBarLegendItem.ARRANGEMENT_LABEL_SYMBOL_DESCRIPTION
        ):
            return "label_symbol_description"
        elif (
            arrangement == HorizontalBarLegendItem.ARRANGEMENT_LABEL_DESCRIPTION_SYMBOL
        ):
            return "label_description_symbol"
        elif (
            arrangement == HorizontalBarLegendItem.ARRANGEMENT_DESCRIPTION_SYMBOL_LABEL
        ):
            return "description_symbol_label"
        elif (
            arrangement == HorizontalBarLegendItem.ARRANGEMENT_DESCRIPTION_LABEL_SYMBOL
        ):
            return "description_label_symbol"
        assert False

    @staticmethod
    def cls_id():
        return "2b65d211-c2c7-11d3-92f3-00600802e603"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.show_heading = True
        self.heading_text_symbol = None
        self.legend_class_format = None
        self.show_labels = True
        self.show_description = True
        self.prevent_column_split = False
        self.arrangement = HorizontalBarLegendItem.ARRANGEMENT_SYMBOL_LABEL_DESCRIPTION
        self.angle_text_above = 0
        self.angle_text_below = 0
        self.show_layer_name = False
        self.layer_name_text_symbol = None
        self.layer = None
        self.group_index = 0
        self.columns = 1
        self.new_column = False

    def read(self, stream: Stream, version):
        internal_version = stream.read_ushort("internal version", expected=(1, 3))

        self.layer = stream.read_object("associated layer")

        self.new_column = stream.read_ushort("new column") != 0
        self.columns = stream.read_ushort("columns")
        self.prevent_column_split = stream.read_ushort("prevent column split") != 0
        self.show_layer_name = stream.read_ushort("show layer name") != 0

        self.layer_name_text_symbol = stream.read_object("layer name text symbol")
        self.group_index = stream.read_int("group index")
        self.show_heading = stream.read_ushort("show heading") != 0
        self.heading_text_symbol = stream.read_object("heading text symbol")
        self.legend_class_format = stream.read_object("legend class format")

        self.show_labels = stream.read_ushort("show labels") != 0
        self.show_description = stream.read_ushort("show description") != 0

        stream.read_int("unknown", expected=0)
        if internal_version > 1:
            stream.read_string("before", expected=" (")
            stream.read_string("after", expected=")")

            stream.read_ushort("unknown", expected=65535)
            stream.read_object("number format")

            self.arrangement = stream.read_int("arrangement")

        self.angle_text_above = stream.read_double("angle text above")
        self.angle_text_below = stream.read_double("angle text below")

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "show_heading": self.show_heading,
            "heading_text_symbol": self.heading_text_symbol.to_dict()
            if self.heading_text_symbol
            else None,
            "legend_class_format": self.legend_class_format.to_dict()
            if self.legend_class_format
            else None,
            "show_labels": self.show_labels,
            "show_description": self.show_description,
            "prevent_column_split": self.prevent_column_split,
            "arrangement": HorizontalBarLegendItem.arrangement_to_string(
                self.arrangement
            ),
            "angle_text_above": self.angle_text_above,
            "angle_text_below": self.angle_text_below,
            "show_layer_name": self.show_layer_name,
            "layer_name_text_symbol": self.layer_name_text_symbol.to_dict()
            if self.layer_name_text_symbol
            else None,
            "layer": self.layer,
            "group_index": self.group_index,
            "columns": self.columns,
            "new_column": self.new_column,
        }
