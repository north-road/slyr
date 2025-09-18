#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream
from .property_set import PropertySet


class EditTemplate(Object):
    """
    EditTemplate
    """

    @staticmethod
    def cls_id():
        return "377035b9-34c7-4a40-866d-e596519a1b06"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.attribute_values = {}
        self.name = ""

    @staticmethod
    def compatible_versions():
        return [2]

    def read(self, stream: Stream, version):
        self.name = stream.read_string("template name")
        stream.read_string("unknown")
        stream.read_raw_clsid("associated tool")

        count = stream.read_int("count")
        for _ in range(count):
            key, value = PropertySet.read_value(stream)
            self.attribute_values[key] = value

        stream.read_string("geometry type?")  # "Line/Polygon"

    def to_dict(self):  # pylint: disable=method-hidden
        return {"name": self.name, "attributes": self.attribute_values}
