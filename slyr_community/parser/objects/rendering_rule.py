#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class RenderingRule(Object):
    """
    RenderingRule
    """

    @staticmethod
    def cls_id():
        return "912fc6f2-4b5f-4aa3-af24-18704ab58f6e"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.name = ""
        self.description = ""
        self.template_arguments = None

    @staticmethod
    def compatible_versions():
        return [2]

    def read(self, stream: Stream, version):
        self.name = stream.read_string("name")
        self.description = stream.read_string("description")
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)

        self.template_arguments = stream.read_object("template arguments")

        stream.read_string("unknown", expected="Raster")
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "name": self.name,
            "description": self.description,
            "template_arguments": self.template_arguments.to_dict()
            if self.template_arguments
            else None,
        }
