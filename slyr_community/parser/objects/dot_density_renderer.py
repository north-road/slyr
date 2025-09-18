#!/usr/bin/env python
"""
Serializable object subclass

NEAR COMPLETE INTERPRETATION - all useful components
"""

from ..object import Object
from ..stream import Stream


class DotDensityRenderer(Object):
    """
    DotDensityRenderer
    """

    @staticmethod
    def cls_id():
        return "9c7776ba-0421-11d4-9f7c-00c04f6bc709"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.fields = []
        self.field_aliases = []
        self.legend_group = None
        self.marker_legend_group = None
        self.ramp_name = ""
        self.fill_symbol = None
        self.exclusion_filter = ""
        self.show_legend_for_excluded = False
        self.legend_group_excluded = None
        self.mask_layer = None
        self.dot_value = 5000
        self.maintain_density_by_dot_value = True
        self.maintain_density = True
        self.min_density = 0
        self.min_density_area = 0
        self.mean_density = 0
        self.mean_area = 0
        self.max_density = 0
        self.max_density_area = 0
        self.scale = 0

    def read(self, stream: Stream, version):
        count = stream.read_int("field count")
        for i in range(count):
            self.fields.append(stream.read_string("field {}".format(i + 1)))
            self.field_aliases.append(stream.read_string("alias"))

        stream.read_ushort("unknown", expected=1)

        self.legend_group_excluded = stream.read_object("legend group for excluded")
        self.exclusion_filter = stream.read_string("exclusion filter")
        self.show_legend_for_excluded = (
            stream.read_ushort("show legend for excluded") != 0
        )

        internal_version = stream.read_ushort("internal version", expected=(2, 3))

        self.dot_value = stream.read_double("dot value")
        self.ramp_name = stream.read_string("ramp name")
        self.fill_symbol = stream.read_object("fill symbol")
        self.mask_layer = stream.read_object("mask layer")

        self.scale = stream.read_double(
            "density calculated at scale"
        )  # , expected=(5063366.408505683, 26581915.20123457))

        self.min_density = stream.read_double("min density")
        self.min_density_area = stream.read_double("min density area")
        self.mean_density = stream.read_double("mean density")
        self.mean_area = stream.read_double("mean area")
        self.max_density = stream.read_double("max density")
        self.max_density_area = stream.read_double("max density area")

        self.maintain_density = stream.read_ushort("no maintain density") == 0

        self.legend_group = stream.read_object("legend group")
        self.marker_legend_group = stream.read_object("marker legends")
        if internal_version > 2:
            self.maintain_density_by_dot_value = (
                stream.read_int("maintain density by") != 0
            )  # esriMaintainDensityBy

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "legend_group_for_excluded": self.legend_group_excluded.to_dict()
            if self.legend_group_excluded
            else None,
            "legend_group": self.legend_group.to_dict() if self.legend_group else None,
            "marker_legend_group": self.marker_legend_group.to_dict()
            if self.marker_legend_group
            else None,
            "ramp_name": self.ramp_name,
            "fill_symbol": self.fill_symbol.to_dict() if self.fill_symbol else None,
            "exclusion_filter": self.exclusion_filter,
            "show_legend_for_excluded": self.show_legend_for_excluded,
            "mask_layer": self.mask_layer,
            "dot_value": self.dot_value,
            "maintain_density_by_dot_value": self.maintain_density_by_dot_value,
            "maintain_density": self.maintain_density,
            "fields": self.fields,
            "field_aliases": self.field_aliases,
            "min_density": self.min_density,
            "min_density_area": self.min_density_area,
            "mean_density": self.mean_density,
            "mean_area": self.mean_area,
            "max_density": self.max_density,
            "max_density_area": self.max_density_area,
            "density_calculated_at_scale": self.scale,
        }
