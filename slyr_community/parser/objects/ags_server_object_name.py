#!/usr/bin/env python
"""
Serializable object subclass

COMPLETE INTERPRETATION
"""

from ...parser.object import Object
from ...parser.stream import Stream


class AgsServerObjectName(Object):
    """
    AgsServerObjectName
    """

    @staticmethod
    def cls_id():
        return "6c22971c-d450-4b4d-9422-ee96a40facc5"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.name = ""
        self.url = ""
        self.connection_name = None
        self.type = ""
        self.parent_type = ""
        self.description = ""
        self.capabilities = ""

    @staticmethod
    def compatible_versions():
        return [2, 3]

    def read(self, stream: Stream, version):
        self.name = stream.read_stringv2("name")
        self.type = stream.read_stringv2(
            "type",
            expected=("ImageServer", "MapServer", "GlobeServer", "FeatureServer"),
        )
        self.url = stream.read_stringv2("url")
        self.connection_name = stream.read_object("connection name")
        self.parent_type = stream.read_stringv2("parent type")
        self.capabilities = stream.read_stringv2("capabilities")
        if version > 2:
            self.description = stream.read_stringv2("description")

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "name": self.name,
            "url": self.url,
            "type": self.type,
            "connection_name": self.connection_name.to_dict()
            if self.connection_name
            else None,
            "parent_type": self.parent_type,
            "description": self.description,
            "capabilities": self.capabilities,
        }
