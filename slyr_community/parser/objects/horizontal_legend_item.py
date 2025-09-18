#!/usr/bin/env python
"""
Serializable object subclass

NEAR COMPLETE INTERPRETATION - all useful components
"""

from .legend_item_base import LegendItemBase
from ..stream import Stream


class HorizontalLegendItem(LegendItemBase):
    """
    HorizontalLegendItem
    """

    @staticmethod
    def cls_id():
        return "a9401a47-4649-11d1-880b-080009ec732a"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    def read(self, stream: Stream, version):
        self.arrangement = stream.read_int("arrangement")
        internal_version = stream.read_ushort("internal version", expected=(1, 2, 3))

        self.layer = stream.read_object("linked layer")  # , expect_existing=True)
        self.place_in_new_column = stream.read_ushort("place in new column") != 0
        self.column_count = stream.read_ushort("column count")

        self.prevent_column_split = stream.read_ushort("prevent column split") != 0
        self.show_layer_name = stream.read_ushort("show layer name") != 0

        self.layer_name_text_symbol = stream.read_object("layer name text symbol")

        self.group_index = stream.read_int("group index")

        self.show_heading = stream.read_ushort("show heading") != 0
        self.heading_text_symbol = stream.read_object("heading text symbol")
        self.legend_class_format = stream.read_object("legend class format")

        self.show_labels = stream.read_ushort("show labels") != 0
        self.show_description = stream.read_ushort("show description") != 0

        if internal_version > 2:
            self.only_show_classes_visible_in_map = (
                stream.read_ushort("only show classes visible in map") != 0
            )

            self.show_feature_count = stream.read_ushort("show feature count") != 0
            self.before_count = stream.read_string("before")
            self.after_count = stream.read_string("after")

            stream.read_ushort("unknown", expected=65535)
            self.count_format = stream.read_object("numeric format")

    def to_dict(self):  # pylint: disable=method-hidden
        res = super().to_dict()
        return res
