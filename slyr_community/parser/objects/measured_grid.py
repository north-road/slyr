#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream
from .units import Units


class MeasuredGrid(Object):
    """
    MeasuredGrid
    """

    @staticmethod
    def cls_id():
        return "03762c90-f4d0-11d1-ade8-080009ec732a"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.name = ""
        self.line_symbol = None
        self.tick_mark_symbol = None
        self.label_format = None
        self.tick_line_symbol = None
        self.tick_length = 0
        self.sub_tick_count = 0
        self.sub_tick_line_symbol = None
        self.sub_tick_length = 0
        self.visible = True
        self.border = None
        self.x_origin = 0
        self.x_interval_size = 0
        self.y_origin = 0
        self.y_interval_size = 0
        self.units = Units.DISTANCE_FEET
        self.fixed_origin = False
        self.crs = None
        self.annotations_left = False
        self.annotations_right = False
        self.annotations_top = False
        self.annotations_bottom = False
        self.major_ticks_left = False
        self.major_ticks_right = False
        self.major_ticks_top = False
        self.major_ticks_bottom = False
        self.minor_ticks_left = False
        self.minor_ticks_right = False
        self.minor_ticks_top = False
        self.minor_ticks_bottom = False

    @staticmethod
    def compatible_versions():
        return [2]

    def read(self, stream: Stream, version):
        stream.read_ushort("unknown", expected=1)
        self.name = stream.read_string("name")
        self.line_symbol = stream.read_object("line symbol")
        self.tick_mark_symbol = stream.read_object("tick mark symbol")
        self.label_format = stream.read_object("label format")
        self.tick_line_symbol = stream.read_object("tick line symbol")
        self.tick_length = stream.read_double("tick length")
        self.sub_tick_count = stream.read_ushort("sub tick count")
        self.sub_tick_line_symbol = stream.read_object("sub tick line symbol")
        self.sub_tick_length = stream.read_double("sub tick length")

        self.visible = stream.read_ushort("visible") != 0

        # 15=all
        # 1 = left
        # 2 = top
        # 4 = right
        # 8 = bottom
        annotation_sides = stream.read_ushort("annotation side flags")
        self.annotations_left = bool(annotation_sides & 1)
        self.annotations_right = bool(annotation_sides & 4)
        self.annotations_top = bool(annotation_sides & 2)
        self.annotations_bottom = bool(annotation_sides & 8)
        major_ticks_sides = stream.read_ushort("major ticks side flags")
        self.major_ticks_left = bool(major_ticks_sides & 1)
        self.major_ticks_right = bool(major_ticks_sides & 4)
        self.major_ticks_top = bool(major_ticks_sides & 2)
        self.major_ticks_bottom = bool(major_ticks_sides & 8)
        minor_ticks_sides = stream.read_ushort("minor ticks side flags")
        self.minor_ticks_left = bool(minor_ticks_sides & 1)
        self.minor_ticks_right = bool(minor_ticks_sides & 4)
        self.minor_ticks_top = bool(minor_ticks_sides & 2)
        self.minor_ticks_bottom = bool(minor_ticks_sides & 8)

        self.border = stream.read_object("border")

        self.x_origin = stream.read_double("x origin")
        self.x_interval_size = stream.read_double("x interval size")
        self.y_origin = stream.read_double("y origin")
        self.y_interval_size = stream.read_double("y interval size")
        self.units = stream.read_int("units")

        self.crs = stream.read_object("crs")
        self.fixed_origin = stream.read_ushort("fixed origin") != 0

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "name": self.name,
            "line_symbol": self.line_symbol.to_dict() if self.line_symbol else None,
            "tick_mark_symbol": self.tick_mark_symbol.to_dict()
            if self.tick_mark_symbol
            else None,
            "label_format": self.label_format.to_dict() if self.label_format else None,
            "tick_line_symbol": self.tick_line_symbol.to_dict()
            if self.tick_line_symbol
            else None,
            "tick_length": self.tick_length,
            "sub_tick_count": self.sub_tick_count,
            "sub_tick_line_symbol": self.sub_tick_line_symbol.to_dict()
            if self.sub_tick_line_symbol
            else None,
            "sub_tick_length": self.sub_tick_length,
            "visible": self.visible,
            "border": self.border.to_dict() if self.border else None,
            "x_origin": self.x_origin,
            "x_interval_size": self.x_interval_size,
            "y_origin": self.y_origin,
            "y_interval_size": self.y_interval_size,
            "units": Units.distance_unit_to_string(self.units),
            "fixed_origin": self.fixed_origin,
            "crs": self.crs.to_dict() if self.crs else None,
            "annotations_left": self.annotations_left,
            "annotations_right": self.annotations_right,
            "annotations_top": self.annotations_top,
            "annotations_bottom": self.annotations_bottom,
            "major_ticks_left": self.major_ticks_left,
            "major_ticks_right": self.major_ticks_right,
            "major_ticks_top": self.major_ticks_top,
            "major_ticks_bottom": self.major_ticks_bottom,
            "minor_ticks_left": self.minor_ticks_left,
            "minor_ticks_right": self.minor_ticks_right,
            "minor_ticks_top": self.minor_ticks_top,
            "minor_ticks_bottom": self.minor_ticks_bottom,
        }
