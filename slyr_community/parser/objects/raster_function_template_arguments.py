#!/usr/bin/env python
"""
Serializable object subclass
"""

from ...parser.object import Object
from ...parser.stream import Stream


class RasterFunctionTemplateArguments(Object):
    """
    RasterFunctionTemplateArguments
    """

    @staticmethod
    def cls_id():
        return "e7e9fa4f-fcc6-483d-9450-ff38b6a2c315"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.properties = None

    def read(self, stream: Stream, version):
        self.properties = stream.read_object("properties")

    def to_dict(self):  # pylint: disable=method-hidden
        return {"properties": self.properties.to_dict() if self.properties else None}
