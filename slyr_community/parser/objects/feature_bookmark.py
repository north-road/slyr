#!/usr/bin/env python
"""
Serializable object subclass

COMPLETE INTERPRETATION
"""

from ..object import Object
from ..stream import Stream


class FeatureBookmark(Object):
    """
    FeatureBookmark
    """

    @staticmethod
    def cls_id():
        return "ec65b35b-4342-11d2-ae22-080009ec732a"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.name = ""
        self.feature_id = 0
        self.feature_class_name = None

    def read(self, stream: Stream, version):
        self.feature_id = stream.read_int("feature id")
        self.feature_class_name = stream.read_object("feature class name")
        self.name = stream.read_string("name")

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "name": self.name,
            "feature_id": self.feature_id,
            "feature_class_name": self.feature_class_name.to_dict()
            if self.feature_class_name
            else None,
        }
