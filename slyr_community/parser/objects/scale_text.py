#!/usr/bin/env python
"""
ScaleText
"""

from ..object import Object
from ..stream import Stream
from .units import Units


class ScaleText(Object):
    """
    ScaleText
    """

    @staticmethod
    def cls_id():
        return "7a3f91dc-b9e3-11d1-8756-0000f8751720"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.text_element = None
        self.relative = False
        self.separator = ""
        self.fixed_aspect_ratio = False
        self.name = ""
        self.map = None
        self.format = ""
        self.page_units = 0
        self.page_unit_label = ""
        self.map_units = 0
        self.map_unit_label = ""
        self.number_format = None

    @staticmethod
    def compatible_versions():
        return [2, 3]

    def read(self, stream: Stream, version):
        internal_version = stream.read_ushort("internal version")

        self.name = stream.read_string("name")
        self.map = stream.read_object("linked map")
        self.fixed_aspect_ratio = stream.read_ushort("fixed aspect ratio") != 0

        if internal_version <= 2:
            stream.read_int("unknown", expected=0)
        elif internal_version > 2:
            stream.read_int("unknown", expected=1)
            stream.read_ushort("unknown", expected=0)
            stream.read_int("unknown", expected=32760)
            stream.read_int("unknown", expected=0)
            stream.read_int("unknown", expected=0)
            stream.read_int("unknown", expected=0)
            stream.read_int("unknown", expected=0)
            stream.read_int("unknown", expected=0)
            stream.read_ushort("unknown", expected=0)
            self.relative = stream.read_int("relative") == 1
        self.format = stream.read_string("format")
        self.page_units = stream.read_int("page units")
        self.map_units = stream.read_int("map units")

        self.text_element = stream.read_object("text element")

        self.page_unit_label = stream.read_string("page unit label")
        self.map_unit_label = stream.read_string("map unit label")
        self.number_format = stream.read_object("numeric format")

        if version > 2:
            self.separator = stream.read_string("separator")

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "relative": self.relative,
            "separator": self.separator,
            "text_element": self.text_element.to_dict() if self.text_element else None,
            "fixed_aspect_ratio": self.fixed_aspect_ratio,
            "name": self.name,
            "map": self.map,
            "format": self.format,
            "page_units": Units.distance_unit_to_string(self.page_units),
            "page_unit_label": self.page_unit_label,
            "map_units": Units.distance_unit_to_string(self.map_units),
            "map_unit_label": self.map_unit_label,
            "number_format": self.number_format.to_dict()
            if self.number_format
            else None,
        }
