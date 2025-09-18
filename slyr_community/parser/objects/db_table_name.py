#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream
from ..object_registry import REGISTRY


class DBTableName(Object):
    """
    DBTableName
    """

    @staticmethod
    def cls_id():
        return "4c9307b2-c125-4497-ba95-aae875553b06"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.name = ""
        self.dataset_name = None
        self.datasource_type = ""
        self.shape_field_name = None
        self.geometry_type = None
        self.crs = None

    @staticmethod
    def compatible_versions():
        return None

    def read(self, stream: Stream, version):
        self.name = stream.read_string("layer name")
        stream.read_string("unknown", expected="")
        self.datasource_type = stream.read_string(
            "data source type", expected=("Table", "Feature Class")
        )
        self.dataset_name = stream.read_object("dataset name")

        self.shape_field_name = stream.read_string("shape field name")
        self.geometry_type = stream.read_int(
            "unknown", expected=(3, 7)
        )  # maybe geometry type?
        self.crs = stream.read_object("crs")

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "name": self.name,
            "dataset_name": self.dataset_name.to_dict() if self.dataset_name else None,
            "datasource_type": self.datasource_type,
            "shape_field_name": self.shape_field_name,
            "geometry_type": self.geometry_type,
            "crs": self.crs.to_dict() if self.crs else None,
        }

    @classmethod
    def from_dict(cls, definition: dict) -> "DBTableName":
        res = DBTableName()
        res.name = definition["name"]
        res.dataset_name = REGISTRY.create_object_from_dict(definition["dataset_name"])
        res.datasource_type = definition["datasource_type"]
        res.shape_field_name = definition.get("shape_field_name")
        res.geometry_type = definition.get("geometry_type")
        res.crs = REGISTRY.create_object_from_dict(definition.get("crs"))
        return res
