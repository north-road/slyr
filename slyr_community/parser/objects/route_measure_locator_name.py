#!/usr/bin/env python
"""
Serializable object subclass
"""

from .units import Units
from ..object import Object
from ..object_registry import REGISTRY
from ..stream import Stream


class RouteMeasureLocatorName(Object):
    """
    RouteMeasureLocatorName
    """

    @staticmethod
    def cls_id():
        return "8cc373a6-2121-11d4-9fc2-00c04f6bdf06"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.name = ""
        self.description = ""
        self.datasource_type = ""
        self.name_string = ""
        self.dataset_name = None
        self.route_id_field_name = ""
        self.route_measure_unit = Units.DISTANCE_METERS

    def read(self, stream: Stream, version):
        stream.read_ushort("unknown", expected=4)
        self.name = stream.read_string("name")
        self.description = stream.read_string("description")
        self.datasource_type = stream.read_string("category")
        self.name_string = stream.read_string("name string")

        self.dataset_name = stream.read_object("feature class name")
        self.route_id_field_name = stream.read_string("route id field name")
        self.route_measure_unit = stream.read_int("route measure unit")

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "name": self.name,
            "description": self.description,
            "datasource_type": self.datasource_type,
            "name_string": self.name_string,
            "feature_class_name": self.dataset_name.to_dict()
            if self.dataset_name
            else None,
            "route_id_field_name": self.route_id_field_name,
            "route_measure_unit": Units.distance_unit_to_string(
                self.route_measure_unit
            ),
        }

    @classmethod
    def from_dict(cls, definition: dict) -> "RouteMeasureLocatorName":
        res = RouteMeasureLocatorName()
        res.name = definition["name"]
        res.description = definition["description"]
        res.datasource_type = definition["datasource_type"]
        res.name_string = definition["name_string"]
        res.dataset_name = REGISTRY.create_object_from_dict(
            definition["feature_class_name"]
        )
        res.route_id_field_name = definition["route_id_field_name"]
        res.route_measure_unit = Units.string_to_distance_unit(
            definition["route_measure_unit"]
        )
        return res
