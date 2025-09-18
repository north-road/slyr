#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..object_registry import REGISTRY
from ..stream import Stream


class Field(Object):
    """
    Field
    """

    @staticmethod
    def cls_id():
        return "f94f7534-9fdf-11d0-bec7-00805f7c4268"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.name = ""
        self.alias = ""
        self.model_name = ""
        self.geometry_def = None
        self.value_domain = None
        self.default_value = None
        self.field_type = 0  # esriFieldType
        self.field_length = 0
        self.precision = 0
        self.scale = 0
        self.editable = False
        self.is_nullable = False
        self.required = False
        self.domain_fixed = False
        self.raster_def = None

    @staticmethod
    def compatible_versions():
        return [2, 3]

    def __repr__(self):
        if self.ref_id is not None:
            return "<Field: {} ({})>".format(self.name, self.ref_id)
        else:
            return "<Field: {}>".format(self.name)

    def read(self, stream: Stream, version):
        stream.read_ushort("unknown", expected=1)
        stream.read_ushort("unknown", expected=65535)
        self.name = stream.read_string("name")

        stream.read_uchar("has alias name", expected=(0, 1))
        self.alias = stream.read_string("alias name")

        stream.read_uchar("has model name", expected=(0, 1))
        self.model_name = stream.read_string("model name")

        stream.read_string(
            "name again?", expected=("", self.name)
        )  # maybe source field?

        stream.read_uchar("has default value", expected=(0, 1))
        var_type = stream.read_ushort("variant type")
        if var_type != 0:
            self.default_value = stream.read_variant(var_type, "default value")

        self.field_type = stream.read_int("field type")
        self.field_length = stream.read_int("field length")
        self.precision = stream.read_int("precision")
        self.scale = stream.read_int("scale")

        _ = stream.read_uchar("required") != 0
        self.is_nullable = stream.read_uchar("is nullable") != 0
        self.editable = stream.read_uchar("editable") != 0
        flags = stream.read_ushort(
            "flags", expected=(0, 1, 256, 257)
        )  # 1 for fid, 0 for geom
        if flags & 1:
            self.required = True
        if flags & 256:
            self.domain_fixed = True

        self.value_domain = stream.read_object("value domain")
        self.geometry_def = stream.read_object("geometry def")

        if version == 2 and self.field_type == 9:
            self.raster_def = stream.read_object("raster def")
        elif version > 2:
            self.raster_def = stream.read_object("raster def")

            if self.raster_def:
                stream.read_object("field")

            stream.read_uchar("unknown", expected=1)

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "name": self.name,
            "alias": self.alias,
            "model_name": self.model_name,
            "default_value": self.default_value,
            "field_type": self.field_type,
            "value_domain": self.value_domain,
            "geometry_definition": self.geometry_def.to_dict()
            if self.geometry_def
            else None,
            "field_length": self.field_length,
            "precision": self.precision,
            "scale": self.scale,
            "editable": self.editable,
            "is_nullable": self.is_nullable,
            "required": self.required,
            "domain_fixed": self.domain_fixed,
            "raster_def": self.raster_def.to_dict() if self.raster_def else None,
        }

    @classmethod
    def from_dict(cls, definition: dict) -> "Field":
        res = Field()
        res.name = definition["name"]
        res.alias = definition["alias"]
        res.model_name = definition["model_name"]
        res.default_value = definition["default_value"]
        res.field_type = definition["field_type"]
        res.value_domain = REGISTRY.create_object_from_dict(definition["value_domain"])
        res.geometry_def = REGISTRY.create_object_from_dict(
            definition["geometry_definition"]
        )
        res.field_length = definition["field_length"]
        res.precision = definition["precision"]
        res.scale = definition["scale"]
        res.editable = definition["editable"]
        res.is_nullable = definition["is_nullable"]
        res.required = definition["required"]
        res.domain_fixed = definition["domain_fixed"]
        res.raster_def = REGISTRY.create_object_from_dict(definition["raster_def"])

        return res
