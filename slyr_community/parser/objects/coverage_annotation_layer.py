#!/usr/bin/env python
"""
Serializable object subclass
"""

from .feature_layer import FeatureLayer
from ..stream import Stream


class CoverageAnnotationLayer(FeatureLayer):
    """
    CoverageAnnotationLayer
    """

    @staticmethod
    def cls_id():
        return "0c22a4c9-dafd-11d2-9f46-00c04f6bc78e"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.symbol_numbers = []
        self.barrier_weight = 0
        self.arrow_symbol = None
        self.fields = []

    @staticmethod
    def compatible_versions():
        return [5]

    def read(self, stream: Stream, version):
        layer_version = stream.read_ushort("layer version")
        super().read(stream, layer_version)

        field_count = stream.read_int("field count")
        for i in range(field_count):
            self.fields.append(stream.read_object("field {}".format(i + 1)))

        stream.read_int("unknown")

        symbol_count = stream.read_int("symbol count")
        for i in range(symbol_count):
            self.symbol_numbers.append(
                stream.read_int("symbol number {}".format(i + 1))
            )

        stream.read_int("unknown", expected=0)

        count = stream.read_int("unknown count")
        for i in range(count):
            stream.read_object("text symbol {}".format(i + 1))

        symbol_count = stream.read_int("text symbol count")
        for i in range(symbol_count):
            stream.read_object("text symbol {}".format(i + 1))

        stream.read_int("unknown", expected=0)

        count = stream.read_int("count")
        for i in range(count):
            stream.read_int("unknown {}".format(i + 1))

        level_count = stream.read_int("level count")
        for i in range(level_count):
            stream.read_ushort("level visibility {}".format(i + 1))

        self.barrier_weight = stream.read_int("barrier weight")
        stream.read_int("unknown", expected=1)

        self.arrow_symbol = stream.read_object("arrow line symbol")

        stream.read_ushort("unknown", expected=0)

        stream.read_object("unknown symbol")
        stream.read_object("unknown symbol")

    def to_dict(self):  # pylint: disable=method-hidden
        res = super().to_dict()
        res["barrier_weight"] = self.barrier_weight
        res["symbol_numbers"] = self.symbol_numbers
        res["arrow_symbol"] = self.arrow_symbol.to_dict() if self.arrow_symbol else None
        res["fields"] = [f.to_dict() for f in self.fields]
        return res
