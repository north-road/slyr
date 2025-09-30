#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class LegendClassFormat(Object):
    """
    LegendClassFormat
    """

    @staticmethod
    def cls_id():
        return "7a3f91e6-b9e3-11d1-8756-0000f8751720"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.label_symbol = None
        self.description_symbol = None
        self.height = 0
        self.width = 0
        self.line_patch_override = None
        self.area_patch_override = None

    @staticmethod
    def compatible_versions():
        return [2]

    def read(self, stream: Stream, version):
        self.label_symbol = stream.read_object("label symbol")
        self.description_symbol = stream.read_object("description symbol")

        self.line_patch_override = stream.read_object("line patch override")
        self.area_patch_override = stream.read_object("area patch override")

        self.width = stream.read_double("width")
        self.height = stream.read_double("height")

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "label_symbol": self.label_symbol.to_dict() if self.label_symbol else None,
            "description_symbol": self.description_symbol.to_dict()
            if self.description_symbol
            else None,
            "height": self.height,
            "width": self.width,
            "area_patch_override": self.area_patch_override.to_dict()
            if self.area_patch_override
            else None,
            "line_patch_override": self.line_patch_override.to_dict()
            if self.line_patch_override
            else None,
        }
