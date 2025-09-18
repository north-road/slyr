#!/usr/bin/env python
"""
Serializable object subclass

NEAR COMPLETE INTERPRETATION - all useful components

"""

from ..stream import Stream
from .vector_renderer import VectorRendererBase


class ChartRenderer(VectorRendererBase):
    """
    ChartRenderer
    """

    @staticmethod
    def cls_id():
        return "4f17939a-c490-11d3-9f7a-00c04f6bc709"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.attributes = []
        self.labels = []
        self.exclusion_filter = ""
        self.show_symbol_for_excluded = False
        self.excluded_legend_group = None
        self.prevent_overlap = True
        self.vary_size_by_attribute = ""
        self.vary_size_using_sum_of_field_values = False
        self.normalize_size_by_attribute = ""
        self.size_normalization_method = VectorRendererBase.NORMALIZE_BY_FIELD
        self.legend_group = None
        self.ramp_name = ""
        self.legend_group = None
        self.class_legend = None
        self.symbol = None
        self.symbol2 = None
        self.size_compensation_flannery = False
        self.vary_size_using_log_of_attribute = False
        self.min_value = 0
        self.min_size = 0

    @staticmethod
    def compatible_versions():
        return [2]

    def read(self, stream: Stream, version):
        stream.read_ushort("unknown", expected=1)

        count = stream.read_int("count")
        for i in range(count):
            attribute = stream.read_string("attribute {}".format(i + 1))
            label = stream.read_string("label {}".format(i + 1))
            self.attributes.append(attribute)
            self.labels.append(label)

        stream.read_ushort("unknown", expected=1)

        self.excluded_legend_group = stream.read_object("excluded legend group")
        self.exclusion_filter = stream.read_string("exclusion filter")
        self.show_symbol_for_excluded = (
            stream.read_ushort("show symbol for excluded") != 0
        )

        for i in range(count):
            stream.read_double(
                "unknown attribute related"
            )  # , expected=(-1, 2216, 94, 34))

        self.symbol = stream.read_object("symbol")
        self.symbol2 = stream.read_object("symbol 2")

        self.ramp_name = stream.read_string("ramp name")

        stream.read_string("unknown", expected="")

        self.prevent_overlap = stream.read_ushort("prevent overlap") != 0
        self.legend_group = stream.read_object("legend group")
        self.class_legend = stream.read_object("class legend group")
        self.vary_size_by_attribute = stream.read_string("vary size using field name")

        stream.read_string("unknown", expected=self.vary_size_by_attribute)

        self.vary_size_using_sum_of_field_values = (
            stream.read_ushort("vary size using sum of field values") != 0
        )
        self.min_value = stream.read_double("min value")
        self.min_size = stream.read_double("min size")
        self.size_compensation_flannery = (
            stream.read_ushort("size compensation flannery") != 0
        )
        self.normalize_size_by_attribute = stream.read_string("normalize by attribute")
        self.vary_size_using_log_of_attribute = stream.read_string("use log") == "<LOG>"
        self.size_normalization_method = stream.read_int("normalize size method")

        stream.read_int("unknown", expected=3)

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "attributes": self.attributes,
            "labels": self.labels,
            "exclusion_filter": self.exclusion_filter,
            "show_symbol_for_excluded": self.show_symbol_for_excluded,
            "prevent_overlap": self.prevent_overlap,
            "vary_size_by_attribute": self.vary_size_by_attribute,
            "vary_size_using_sum_of_field_values": self.vary_size_using_sum_of_field_values,
            "normalize_size_by_attribute": self.normalize_size_by_attribute,
            "size_normalization_method": VectorRendererBase.normalize_method_to_string(
                self.size_normalization_method
            ),
            "excluded_legend_group": self.excluded_legend_group.to_dict()
            if self.excluded_legend_group
            else None,
            "ramp_name": self.ramp_name,
            "legend_group": self.legend_group.to_dict() if self.legend_group else None,
            "class_legend": self.class_legend.to_dict() if self.class_legend else None,
            "symbol": self.symbol.to_dict() if self.symbol else None,
            "symbol2": self.symbol2.to_dict() if self.symbol2 else None,
            "size_compensation_flannery": self.size_compensation_flannery,
            "vary_size_using_log_of_attribute": self.vary_size_using_log_of_attribute,
            "min_value": self.min_value,
            "min_size": self.min_size,
        }
