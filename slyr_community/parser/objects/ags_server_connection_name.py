#!/usr/bin/env python
"""
Serializable object subclass

COMPLETE INTERPRETATION
"""

from ...parser.object import Object
from ...parser.stream import Stream


class AgsServerConnectionName(Object):
    """
    AgsServerConnectionName
    """

    @staticmethod
    def cls_id():
        return "cba35c3f-edef-408f-8b51-510784c78eb9"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.properties = None
        self.name = ""

    @staticmethod
    def compatible_versions():
        return [1, 2]

    def read(self, stream: Stream, version):
        self.properties = stream.read_object("properties")
        if version > 1:
            self.name = stream.read_string("name")

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "properties": self.properties.to_dict() if self.properties else None,
            "name": self.name,
        }
