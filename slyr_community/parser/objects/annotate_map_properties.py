#!/usr/bin/env python
"""
Serializable object subclass

COMPLETE INTERPRETATION
"""

from ..object import Object
from ..stream import Stream


class AnnotateMapProperties(Object):
    """
    AnnotateMapProperties
    """

    @staticmethod
    def cls_id():
        return "8c439001-14ec-11d2-a27e-080009b6f22b"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.annotate_layer_properties_collection = None

    def read(self, stream: Stream, version):
        self.annotate_layer_properties_collection = stream.read_object(
            "annotate layer properties collection"
        )

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "annotate_layer_properties_collection": self.annotate_layer_properties_collection.to_dict()
            if self.annotate_layer_properties_collection
            else None
        }
