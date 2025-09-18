#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class StackedChartSymbol(Object):
    """
    StackedChartSymbol
    """

    @staticmethod
    def cls_id():
        return "50317369-bd70-11d3-9f79-00c04f6bc709"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.max_length = 0
        self.display_in_3d = False
        self.thickness = 0
        self.symbols = []
        self.callout = None
        self.bar_width = 8
        self.show_outline = False
        self.outline = None
        self.fixed_length = False
        self.orientation_vertical = True
        self.max_value = 0
        self.x_offset = 0
        self.y_offset = 0
        self.values = []

    def read(self, stream: Stream, version):
        self.max_length = stream.read_double("max length")

        stream.read_double("unknown", expected=90)  # probably tilt

        self.x_offset = stream.read_double("x offset")
        self.y_offset = stream.read_double("y offset")

        self.display_in_3d = stream.read_uchar("display in 3d") != 0
        self.thickness = stream.read_double("thickness")

        self.show_outline = stream.read_uchar("show outline") != 0
        self.orientation_vertical = stream.read_uchar("orientation vertical") != 0
        self.fixed_length = stream.read_uchar("fixed length") != 0
        self.bar_width = stream.read_double("bar width")
        self.outline = stream.read_object("outline")

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
            "display_in_3d": self.display_in_3d,
            "thickness": self.thickness,
            "symbols": [s.to_dict() for s in self.symbols],
            "callout": self.callout.to_dict() if self.callout else None,
            "bar_width": self.bar_width,
            "show_outline": self.show_outline,
            "outline": self.outline.to_dict() if self.outline else None,
            "fixed_length": self.fixed_length,
            "orientation_vertical": self.orientation_vertical,
            "max_value": self.max_value,
            "x_offset": self.x_offset,
            "y_offset": self.y_offset,
            "values": self.values,
        }
