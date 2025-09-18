#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream
from .units import Units


class RouteMeasurePointProperties(Object):
    """
    RouteMeasurePointProperties
    """

    @staticmethod
    def cls_id():
        return "c13d6537-3c80-11d4-9fcd-00c04f6bdf06"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.event_route_id_field = ""
        self.measure_field_name = ""
        self.lateral_offset_field_name = ""
        self.event_measure_unit = 0
        self.add_error_field = False
        self.error_field_name = ""
        self.as_point_feature = False
        self.add_angle_field = False
        self.angle_field = ""
        self.normal_angle = False
        self.complement_angle = False

    @staticmethod
    def compatible_versions():
        return [5]

    def read(self, stream: Stream, version):
        self.event_route_id_field = stream.read_string("event route id field name")
        self.measure_field_name = stream.read_string("from measure field name")
        stream.read_string("unknown", expected="")
        self.lateral_offset_field_name = stream.read_string("lateral offset field name")
        stream.read_uchar("unknown", expected=0)
        self.event_measure_unit = stream.read_int("event measure unit")
        self.add_error_field = stream.read_ushort("add error field") != 0
        self.error_field_name = stream.read_string("error field name")
        stream.read_ushort("unknown", expected=65535)
        self.as_point_feature = stream.read_ushort("as point feature") != 0
        self.add_angle_field = stream.read_ushort("add angle field") != 0
        self.angle_field = stream.read_string("angle field")
        self.normal_angle = stream.read_ushort("normal angle") != 0
        self.complement_angle = stream.read_ushort("complement angle") != 0

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "event_route_id_field": self.event_route_id_field,
            "measure_field_name": self.measure_field_name,
            "lateral_offset_field_name": self.lateral_offset_field_name,
            "event_measure_unit": Units.distance_unit_to_string(
                self.event_measure_unit
            ),
            "add_error_field": self.add_error_field,
            "error_field_name": self.error_field_name,
            "as_point_feature": self.as_point_feature,
            "add_angle_field": self.add_angle_field,
            "angle_field": self.angle_field,
            "normal_angle": self.normal_angle,
            "complement_angle": self.complement_angle,
        }
