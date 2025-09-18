#!/usr/bin/env python
"""
Serializable object subclass
"""

from .element import Element
from ..stream import Stream


class Legend(Element):
    """
    Legend
    """

    @staticmethod
    def cls_id():
        return "7a3f91e4-b9e3-11d1-8756-0000f8751720"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.title = ""
        self.linked_map = None
        self.format = None
        self.label_width = 0
        self.description_width = 0
        self.add_new_items_to_legend_when_added_to_map = False
        self.reorder_when_map_layers_reordered = False
        self.show_only_layers_checked_in_toc = False
        self.scale_symbols_when_reference_scale_set = False
        self.fixed_frame = False
        self.auto_adjust_number_columns = False
        self.shrink_contents_to_fit_frame = False
        self.min_font_size = False
        self.items = []
        self.right_to_left = False

    @staticmethod
    def compatible_versions():
        return [2, 3, 4, 5]

    def read(self, stream: Stream, version):
        internal_version = stream.read_ushort("internal version", expected=(1, 2, 3))

        self.element_name = stream.read_string("element name")
        self.linked_map = stream.read_object("linked map")  # , expect_existing=True)

        if internal_version > 2:
            stream.read_ushort("unknown", expected=(0, 65535))
            stream.read_int("unknown", expected=1)
            stream.read_ushort("unknown", expected=0)

            stream.read_int("unknown", expected=(2147516408, 32760))
            stream.read_int("unknown", expected=(0, 1401877325))
            stream.read_int("unknown", expected=(0, 2684370918))
            stream.read_int("unknown", expected=(0, 134002979))
            stream.read_int("unknown", expected=(0, 2415935514))
            stream.read_int("unknown", expected=(0, 2956655486))

        if version > 2:
            stream.read_ushort("unknown", expected=(0, 16422))

        self.format = stream.read_object("legend format")

        # may belong in LegendFormat?
        stream.read_ushort("unknown", expected=65535)

        if version > 4:
            self.label_width = stream.read_double("label width for wrapping")
            self.description_width = stream.read_double(
                "description width for wrapping"
            )

        self.title = stream.read_string("title")

        self.add_new_items_to_legend_when_added_to_map = (
            stream.read_ushort("add new items to legend when added to map") != 0
        )
        self.reorder_when_map_layers_reordered = (
            stream.read_ushort("reorder when map layers reordered") != 0
        )
        self.show_only_layers_checked_in_toc = (
            stream.read_ushort("show only layers checked in toc") != 0
        )
        stream.read_ushort("unknown", expected=(0, 47, 71, 49240, 65535))

        count = stream.read_int("count")
        for i in range(count):
            self.items.append(stream.read_object("item {}".format(i + 1)))

        if version > 2:
            self.right_to_left = stream.read_ushort("right to left") != 0

        if version > 3:
            self.scale_symbols_when_reference_scale_set = (
                stream.read_ushort("scale symbols when reference scale set") != 0
            )

        if version > 4:
            self.fixed_frame = stream.read_ushort("fixed frame") != 0
            self.auto_adjust_number_columns = (
                stream.read_ushort("auto adjust number columns") != 0
            )
            self.shrink_contents_to_fit_frame = (
                stream.read_ushort("shrink contents to fit frame") != 0
            )
            self.min_font_size = stream.read_double("min font size")

    def to_dict(self):  # pylint: disable=method-hidden
        res = super().to_dict()
        res["title"] = self.title
        res["linked_map"] = self.linked_map
        res["format"] = self.format.to_dict() if self.format else None
        res["label_width_for_wrapping"] = self.label_width
        res["description_width_for_wrapping"] = self.description_width
        res["add_new_items_to_legend_when_added_to_map"] = (
            self.add_new_items_to_legend_when_added_to_map
        )
        res["reorder_when_map_layers_reordered"] = (
            self.reorder_when_map_layers_reordered
        )
        res["show_only_layers_checked_in_toc"] = self.show_only_layers_checked_in_toc
        res["scale_symbols_when_reference_scale_set"] = (
            self.scale_symbols_when_reference_scale_set
        )
        res["fixed_frame"] = self.fixed_frame
        res["auto_adjust_number_columns"] = self.auto_adjust_number_columns
        res["shrink_contents_to_fit_frame"] = self.shrink_contents_to_fit_frame
        res["min_font_size"] = self.min_font_size
        res["items"] = [i.to_dict() for i in self.items]
        res["right_to_left"] = self.right_to_left
        return res
