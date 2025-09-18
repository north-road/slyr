#!/usr/bin/env python
"""
Serializable object subclass
"""

from .scalebar_base import ScalebarBase
from ..stream import Stream


class ScaleLine(ScalebarBase):
    """
    ScaleLine
    """

    @staticmethod
    def cls_id():
        return "6589f140-f7f7-11d2-b872-00600802e603"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    def read(self, stream: Stream, version):
        super()._read(stream, version, "Scale Line")

        self.bar_line_symbol = stream.read_object("bar line symbol")

        stream.read_ushort("unknown", expected=2)

        self.division_line_symbol = stream.read_object("division line symbol")
        self.sub_division_line_symbol = stream.read_object("subdivision line symbol")
        self.division_height = stream.read_double("division height")
        self.sub_division_height = stream.read_double("subdivision height")
        self.mark_position = stream.read_int("mark position")
        self.mark_frequency = stream.read_int("mark frequency")

    def to_dict(self):  # pylint: disable=method-hidden
        res = super().to_dict()
        return res
