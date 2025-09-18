#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream
from .units import Units


class RouteMeasureLineProperties(Object):
    """
    RouteMeasureLineProperties
    """

    @staticmethod
    def cls_id():
        return "35bdf2f0-3b21-11d4-9fcb-00c04f6bdf06"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.event_route_id_field = ""
        self.from_measure_field_name = ""
        self.to_measure_field_name = ""
        self.lateral_offset_field_name = ""
        self.event_measure_unit = 0
        self.add_error_field = False
        self.error_field_name = ""
        self.m_direction_offsetting = False

    @staticmethod
    def compatible_versions():
        return [5]

    def read(self, stream: Stream, version):
        self.event_route_id_field = stream.read_string("event route id field name")
        self.from_measure_field_name = stream.read_string("from measure field name")
        self.to_measure_field_name = stream.read_string("to measure field name")
        self.lateral_offset_field_name = stream.read_string("lateral offset field name")
        stream.read_uchar("unknown", expected=1)
        self.event_measure_unit = stream.read_int("event measure unit")
        self.add_error_field = stream.read_ushort("add error field") != 0
        self.error_field_name = stream.read_string("error field name")
        self.m_direction_offsetting = stream.read_ushort("m direction offsetting") != 0

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "event_route_id_field": self.event_route_id_field,
            "from_measure_field_name": self.from_measure_field_name,
            "to_measure_field_name": self.to_measure_field_name,
            "lateral_offset_field_name": self.lateral_offset_field_name,
            "event_measure_unit": Units.distance_unit_to_string(
                self.event_measure_unit
            ),
            "add_error_field": self.add_error_field,
            "error_field_name": self.error_field_name,
            "m_direction_offsetting": self.m_direction_offsetting,
        }

    @classmethod
    def from_dict(cls, definition: dict) -> "RouteMeasureLineProperties":
        res = RouteMeasureLineProperties()
        res.event_route_id_field = definition["event_route_id_field"]
        res.from_measure_field_name = definition["from_measure_field_name"]
        res.to_measure_field_name = definition["to_measure_field_name"]
        res.lateral_offset_field_name = definition["lateral_offset_field_name"]
        res.event_measure_unit = Units.string_to_distance_unit(
            definition["event_measure_unit"]
        )
        res.add_error_field = definition["add_error_field"]
        res.error_field_name = definition["error_field_name"]
        res.m_direction_offsetting = definition["m_direction_offsetting"]
        return res
