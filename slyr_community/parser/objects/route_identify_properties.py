#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class RouteIdentifyProperties(Object):
    """
    RouteIdentifyProperties
    """

    @staticmethod
    def cls_id():
        return "f96f4050-0e8f-4504-acdf-784e4d240509"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.measure_label = None
        self.maximum_measure_label = None
        self.minimum_measure_label = None
        self.parts_label = None
        self.unknown_measures_label = None
        self.measure_value_label = None

    def read(self, stream: Stream, version):
        self.measure_label = stream.read_string("measure label")
        self.maximum_measure_label = stream.read_string("maximum measure label")
        self.minimum_measure_label = stream.read_string("minimum measure label")
        self.parts_label = stream.read_string("parts label")
        self.unknown_measures_label = stream.read_string("unknown measures label")
        self.measure_value_label = stream.read_string("measure value label")

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "measure_label": self.measure_label,
            "maximum_measure_label": self.maximum_measure_label,
            "minimum_measure_label": self.minimum_measure_label,
            "parts_label": self.parts_label,
            "unknown_measures_label": self.unknown_measures_label,
            "measure_value_label": self.measure_value_label,
        }
