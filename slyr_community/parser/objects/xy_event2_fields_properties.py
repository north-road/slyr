#!/usr/bin/env python
"""
XYEvent2FieldsProperties

COMPLETE INTERPRETATION
"""

from ..object import Object
from ..stream import Stream


class XYEvent2FieldsProperties(Object):
    """
    XYEvent2FieldsProperties
    """

    @staticmethod
    def cls_id():
        return "71045ca2-7902-11d4-9fe5-00c04f6bdf06"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.x_field = ""
        self.y_field = ""
        self.z_field = ""

    def read(self, stream: Stream, version):
        self.x_field = stream.read_string("x")
        self.y_field = stream.read_string("y")
        self.z_field = stream.read_string("z")

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "x_field": self.x_field,
            "y_field": self.y_field,
            "z_field": self.z_field,
        }

    @classmethod
    def from_dict(cls, definition: dict) -> "XYEvent2FieldsProperties":
        res = XYEvent2FieldsProperties()
        res.x_field = definition["x_field"]
        res.y_field = definition["y_field"]
        res.z_field = definition["z_field"]
        return res
