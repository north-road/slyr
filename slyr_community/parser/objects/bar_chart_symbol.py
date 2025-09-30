#!/usr/bin/env python
"""
Serializable object subclass

COMPLETE INTERPRETATION
"""

from ..object import Object
from ..stream import Stream


class BarChartSymbol(Object):
    """
    BarChartSymbol
    """

    @staticmethod
    def cls_id():
        return "5031736a-bd70-11d3-9f79-00c04f6bc709"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.max_length = 0
        self.spacing = 0
        self.bar_width = 0
        self.display_in_3d = False
        self.thickness = 0
        self.symbols = []
        self.axis_symbol = None
        self.callout = None
        self.show_axis = False
        self.orientation_vertical = True
        self.values = []
        self.max_value = 0
        self.x_offset = 0
        self.y_offset = 0

    def read(self, stream: Stream, version):
        self.max_length = stream.read_double("max length")

        # probably tilt
        stream.read_double("unknown", expected=90)

        self.x_offset = stream.read_double("x offset")
        self.y_offset = stream.read_double("y offset")

        self.display_in_3d = stream.read_uchar("display in 3d") != 0
        self.thickness = stream.read_double("thickness")

        self.show_axis = stream.read_uchar("show axis") != 0
        self.orientation_vertical = stream.read_uchar("orientation vertical") != 0

        self.spacing = stream.read_double("spacing")
        self.bar_width = stream.read_double("bar width")
        self.axis_symbol = stream.read_object("axis_symbol")

        stream.read_ushort("unknown", expected=2)

        stream.read_int("raster op code")

        stream.read_int("unknown", expected=0)
        self.max_value = stream.read_double("max value")

        count = stream.read_int("count")
        for i in range(count):
            self.symbols.append(stream.read_object("fill symbol {}".format(i + 1)))
            self.values.append(stream.read_double("value {}".format(i + 1)))

        self.callout = stream.read_object("line callout")

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "max_length": self.max_length,
            "spacing": self.spacing,
            "bar_width": self.bar_width,
            "display_in_3d": self.display_in_3d,
            "thickness": self.thickness,
            "symbols": [s.to_dict() for s in self.symbols],
            "axis_symbol": self.axis_symbol.to_dict() if self.axis_symbol else None,
            "callout": self.callout.to_dict() if self.callout else None,
            "show_axis": self.show_axis,
            "orientation_vertical": self.orientation_vertical,
            "values": self.values,
            "max_value": self.max_value,
            "x_offset": self.x_offset,
            "y_offset": self.y_offset,
        }
