#!/usr/bin/env python
"""
Serializable object subclass
"""

from .raster_renderer import RasterRenderer
from ..stream import Stream


class RasterUniqueValueRenderer(RasterRenderer):
    """
    RasterUniqueValueRenderer
    """

    @staticmethod
    def cls_id():
        return "0842b595-4f2f-11d2-9f43-00c04f8ece3d"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.ramp_name = ""
        self.value_name = ""
        self.all_other_values_checked = False
        self.all_other_symbol = None
        self.all_other_legend_label = ""
        self.legend_groups = []
        self.ramp = None
        self.unique_values = None
        self.values = []
        self.backup_value_count = []

    @staticmethod
    def compatible_versions():
        return [1, 2, 3, 4]

    def read(self, stream: Stream, version):
        self.should_read_display_props = version > 1

        # BAND??
        # Invert Ramp??
        stream.read_ushort("unknown", expected=0)

        self.value_name = stream.read_string("value name")
        if version > 2:
            stream.read_string("unknown")  # "value", "descriptio"?
        self.ramp_name = stream.read_string("ramp name")
        self.all_other_values_checked = (
            stream.read_ushort("all other values checked") != 0
        )

        self.all_other_symbol = stream.read_object("all other symbol")
        self.all_other_legend_label = stream.read_string("all other legend label")

        if version <= 2:
            stream.read_int("older value count?")

        count = stream.read_int("group count")
        for i in range(count):
            self.legend_groups.append(
                stream.read_object("legend group {}".format(i + 1))
            )

        if version <= 2:
            stream.read_double("unknown", expected=0)
            stream.read_double("unknown", expected=0)

        num_values = 0
        count = stream.read_int("count")
        for i in range(count):
            # 65536 for groups!
            if version == 1:
                stream.read_ushort("unknown", expected=0)
                value_count = stream.read_ushort("value count")
            else:
                stream.read_int("index", expected=(i, 65536))

            value_count = stream.read_int("value count")

            values = []
            for j in range(value_count):
                num_values += 1
                # variant type
                value_type = stream.read_ushort(
                    "value type {}".format(j + 1), expected=(5, 8)
                )

                stream.read_ushort("unknown {}".format(j + 1))  # , expected=0)
                stream.read_int("unknown {}".format(j + 1))  # , expected=0)

                stream.read_double("unknown {}".format(j + 1))  # , expected=0) value??

                values.append(stream.read_variant(value_type, "value {}".format(j + 1)))

            if values:
                self.values.append(values)

        stream.read_ushort("unknown", expected=0)
        self.unique_values = stream.read_object("unique values")

        if version > 3:
            self.ramp = stream.read_object("color ramp")

        # maybe here for other versions too?
        elif not self.unique_values:
            prev_count = count
            count = stream.read_int("value count", expected=prev_count)
            for i in range(count):
                v = stream.read_double("value {}".format(i + 1))
                c = stream.read_int("count")
                self.backup_value_count.append([v, c])

        super().read(stream, None)

    def to_dict(self):  # pylint: disable=method-hidden
        res = super().to_dict()
        res["ramp_name"] = self.ramp_name
        res["value_name"] = self.value_name
        res["all_other_values_checked"] = self.all_other_values_checked
        res["all_other_symbol"] = (
            self.all_other_symbol.to_dict() if self.all_other_symbol else None
        )
        res["all_other_legend_label"] = self.all_other_legend_label
        res["legend_groups"] = [g.to_dict() for g in self.legend_groups]
        res["ramp"] = self.ramp.to_dict() if self.ramp else None
        res["unique_values"] = (
            self.unique_values.to_dict() if self.unique_values else None
        )
        res["values"] = self.values
        res["backup_value_count"] = self.backup_value_count
        return res
