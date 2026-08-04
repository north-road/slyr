#!/usr/bin/env python
"""
Serializable object subclass

COMPLETE INTERPRETATION
"""

from ..object import Object
from ..stream import Stream


class AOIBookmark(Object):
    """
    AOIBookmark
    """

    @staticmethod
    def cls_id():
        return "bbb1ae73-41e3-11d2-ae1e-080009ec732a"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.extent = None
        self.name = ""

    def read(self, stream: Stream, version):
        self.extent = stream.read_object("envelope")
        self.name = stream.read_string("name")

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "name": self.name,
            "extent": self.extent.to_dict() if self.extent else None,
        }
