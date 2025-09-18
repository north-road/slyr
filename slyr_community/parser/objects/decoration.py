#!/usr/bin/env python
"""
Line decorations

COMPLETE INTERPRETATION
"""

from ..object import Object
from ..stream import Stream


class LineDecoration(Object):
    """
    Line decoration, consisting of a number of decoration elements
    """

    @staticmethod
    def cls_id():
        return "533d88f5-0a1a-11d2-b27f-0000f878229e"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.decorations = []

    def to_dict(self):  # pylint: disable=method-hidden
        out = {"decorations": []}
        for d in self.decorations:
            if d is not None:
                out["decorations"].append(d.to_dict())
        return out

    def children(self):
        res = super().children()
        res.extend(self.decorations)
        return res

    def read(self, stream: Stream, version):
        """
        Reads the decoration information
        """
        # next bit is probably number of decorations?
        count = stream.read_uint("count of decorations")
        for i in range(count):
            decoration = stream.read_object("decoration element {}/{}".format(i, count))
            self.decorations.append(decoration)


class SimpleLineDecorationElement(Object):
    """
    ISimpleLineDecorationElement
    """

    @staticmethod
    def cls_id():
        return "533d88f3-0a1a-11d2-b27f-0000f878229e"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.fixed_angle = False
        self.flip_first = False
        self.flip_all = False
        self.marker = None
        self.marker_positions = []
        self.position_as_ratio = True

    def to_dict(self):  # pylint: disable=method-hidden
        out = {
            "fixed_angle": self.fixed_angle,
            "flip_first": self.flip_first,
            "flip_all": self.flip_all,
            "marker": None,
            "positions": self.marker_positions,
            "position_as_ratio": self.position_as_ratio,
        }

        if self.marker is not None:
            out["marker"] = self.marker.to_dict()

        return out

    def children(self):
        res = super().children()
        if self.marker:
            res.append(self.marker)
        return res

    def read(self, stream: Stream, version):
        """
        Reads the decoration information
        """
        self.fixed_angle = not bool(stream.read_uchar())
        stream.log(
            "detected {}".format(
                "fixed angle" if self.fixed_angle else "not fixed angle"
            )
        )
        self.flip_first = bool(stream.read_uchar())
        stream.log(
            "detected {}".format("flip first" if self.flip_first else "no flip first")
        )
        self.flip_all = bool(stream.read_uchar())
        stream.log("detected {}".format("flip all" if self.flip_all else "no flip all"))

        self.position_as_ratio = stream.read_ushort("position as ratio") != 0

        self.marker = stream.read_object("marker")

        # next bit is the number of doubles coming next
        marker_number_positions = stream.read_uint("marker positions")

        # next bit is the positions themselves -- maybe we can infer this from the number of positions
        # alone. E.g. 2 positions = 0, 1. 3 positions = 0, 0.5, 1
        for _ in range(marker_number_positions):
            self.marker_positions.append(stream.read_double())
        stream.log("marker positions are {}".format(self.marker_positions))
