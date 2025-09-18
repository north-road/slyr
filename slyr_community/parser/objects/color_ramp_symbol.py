#!/usr/bin/env python
"""
Serializable object subclass

NEAR COMPLETE INTERPRETATION - all useful components
"""

from ..object import Object
from ..stream import Stream


class ColorRampSymbol(Object):
    """
    ColorRampSymbol
    """

    @staticmethod
    def cls_id():
        return "40987040-204c-11d3-a3f2-0004ac1b1d86"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.color = None
        self.color_ramp = None
        self.legend_class_index = 0
        self.invert = False
        self.number_of_label = 0
        self.horizontal = False
        self.show_ticks = True

    @staticmethod
    def compatible_versions():
        return [2, 3, 5]

    def read(self, stream: Stream, version):
        self.color = stream.read_object("color")

        stream.read_int("raster op", expected=13)
        stream.read_int("unknown", expected=0)
        stream.read_int(
            "unknown"
        )  # expected=(0,194149600, 239970880, 324278056, 6757008) )

        self.color_ramp = stream.read_object("color ramp")

        self.invert = stream.read_ushort("invert") != 0
        self.legend_class_index = stream.read_int("legend class index")
        if 2 < version < 5:
            stream.read_int("unknown", expected=0)
            stream.read_ushort("unknown", expected=0)
        elif version >= 5:
            stream.read_ushort("unknown", expected=0)
            stream.read_int("unknown", expected=0)
            self.number_of_label = stream.read_int("number of labels")
            self.horizontal = stream.read_ushort("horizontal") != 0
            self.show_ticks = stream.read_ushort("show ticks") != 0

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "color": self.color.to_dict() if self.color else None,
            "color_ramp": self.color_ramp.to_dict() if self.color_ramp else None,
            "legend_class_index": self.legend_class_index,
            "invert": self.invert,
            "number_of_labels": self.number_of_label,
            "horizontal": self.horizontal,
            "show_ticks": self.show_ticks,
        }
