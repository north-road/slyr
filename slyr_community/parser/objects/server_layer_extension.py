#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class ServerLayerExtension(Object):
    """
    ServerLayerExtension
    """

    @staticmethod
    def cls_id():
        return "f7fd0ec9-f215-4e7f-b1f8-94ba0eb603b9"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.properties = None

    def read(self, stream: Stream, version):
        self.properties = stream.read_object("server properties")

    def to_dict(self):  # pylint: disable=method-hidden
        return {"properties": self.properties.to_dict() if self.properties else None}
