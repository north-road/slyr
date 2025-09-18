#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class RasterBandCollectionName(Object):
    """
    RasterBandCollectionName
    """

    @staticmethod
    def cls_id():
        return "710fc1b5-a118-445b-98d4-ef7d56e18a88"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    def read(self, stream: Stream, version):
        # possibly these are in GenericRaster
        stream.read_string("unknown", expected="")
        stream.read_object("dataset name")
        stream.read_object("band array?")

    def to_dict(self):  # pylint: disable=method-hidden
        return {}
