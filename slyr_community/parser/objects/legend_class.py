#!/usr/bin/env python
"""
LegendClass

Represents a single entry in a legend

COMPLETE INTERPRETATION
"""

from ..object import Object
from ..stream import Stream


class LegendClass(Object):
    """
    LegendClass
    """

    @staticmethod
    def cls_id():
        return "167c5ea3-af20-11d1-8817-080009ec732a"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.symbol = None
        self.format = None
        self.label = None  # shows in table of contents
        self.description = None  # shows in legend
        self.feature_count = None

    @staticmethod
    def compatible_versions():
        return [1, 2]

    def read(self, stream: Stream, version):
        self.symbol = stream.read_object("symbol")
        self.label = stream.read_string("label")
        self.description = stream.read_string("description")
        self.format = stream.read_object("format")
        if version == 2:
            count = stream.read_int("feature count")
            self.feature_count = count if count != 0xFFFFFFFF else None

    def children(self):
        res = super().children()
        if self.symbol:
            res.extend(self.symbol)
        if self.format:
            res.extend(self.format)
        return res

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "symbol": self.symbol.to_dict() if self.symbol else None,
            "format": self.format.to_dict() if self.format else None,
            "label": self.label,
            "description": self.description,
            "feature_count": self.feature_count,
        }
