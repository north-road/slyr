#!/usr/bin/env python
"""
Serializable object subclass
"""

from ...parser.object import Object
from ...parser.stream import Stream


class MosaicRule(Object):
    """
    MosaicRule
    """

    NONE = 0
    CLOSEST_TO_CENTER = 1
    CLOSEST_NADIR = 2
    CLOSEST_TO_VIEWPOINT = 3
    BY_ATTRIBUTE = 4
    LOCK_RASTER_ID = 5
    NORTH_WEST = 6
    SEAMLINE = 7

    OPERATOR_FIRST = 1
    OPERATOR_LAST = 2
    OPERATOR_MIN = 3
    OPERATOR_MAX = 4
    OPERATOR_MEAN = 5
    OPERATOR_BLEND = 6
    OPERATOR_SUM = 7

    @staticmethod
    def cls_id():
        return "33638700-d926-4ecd-9ce9-bcaa96e8e89c"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.field = ""
        self.method = MosaicRule.CLOSEST_NADIR
        self.operator = MosaicRule.OPERATOR_MIN
        self.point = None
        self.raster_id = ""
        self.order_base_value = ""
        self.ascending = True

    @staticmethod
    def compatible_versions():
        return [5, 6]

    @staticmethod
    def operator_to_string(operator):
        if operator == MosaicRule.OPERATOR_FIRST:
            return "first"
        elif operator == MosaicRule.OPERATOR_LAST:
            return "last"
        elif operator == MosaicRule.OPERATOR_MIN:
            return "min"
        elif operator == MosaicRule.OPERATOR_MAX:
            return "max"
        elif operator == MosaicRule.OPERATOR_MEAN:
            return "mean"
        elif operator == MosaicRule.OPERATOR_BLEND:
            return "blend"
        elif operator == MosaicRule.OPERATOR_SUM:
            return "sum"
        assert False, operator

    @staticmethod
    def method_to_string(method):
        if method == MosaicRule.NONE:
            return "none"
        elif method == MosaicRule.CLOSEST_TO_CENTER:
            return "closest_to_center"
        elif method == MosaicRule.CLOSEST_NADIR:
            return "closest_to_nadir"
        elif method == MosaicRule.CLOSEST_TO_VIEWPOINT:
            return "closest_to_viewpoint"
        elif method == MosaicRule.BY_ATTRIBUTE:
            return "by_attribute"
        elif method == MosaicRule.NORTH_WEST:
            return "north_west"
        elif method == MosaicRule.LOCK_RASTER_ID:
            return "lock_raster_id"
        elif method == MosaicRule.SEAMLINE:
            return "seamline"

        assert False, method

    def read(self, stream: Stream, version):
        stream.read_string("unknown", expected="")
        self.field = stream.read_string("field")

        if stream.read_int("unknown", expected=(0, 8)) != 0:
            stream.read_int("unknown", expected=0)
            stream.read_int("unknown", expected=0)
            stream.read_int("unknown", expected=0)
            self.order_base_value = stream.read_string("order base value")
        else:
            stream.read_int("unknown", expected=0)
            stream.read_int("unknown", expected=0)
            stream.read_int("unknown", expected=0)

        self.raster_id = stream.read_string("raster id")

        self.ascending = stream.read_ushort("ascending") != 0

        self.method = stream.read_int("method")
        self.operator = stream.read_int("operator")

        self.point = stream.read_object("point")

        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)

        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)

        if version > 5:
            stream.read_int("unknown", expected=0)
            stream.read_int("unknown", expected=0)
            stream.read_int("unknown", expected=0)
            stream.read_int("unknown", expected=0)

            stream.read_int("unknown", expected=0)
            stream.read_int("unknown", expected=0)
            stream.read_int("unknown", expected=0)
            stream.read_int("unknown", expected=0)

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "field": self.field,
            "method": MosaicRule.method_to_string(self.method),
            "point": self.point.to_dict() if self.point else None,
            "raster_id": self.raster_id,
            "operator": MosaicRule.operator_to_string(self.operator),
            "order_base_value": self.order_base_value,
            "ascending": self.ascending,
        }
