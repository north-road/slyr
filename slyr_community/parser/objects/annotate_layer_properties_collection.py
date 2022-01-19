#!/usr/bin/env python
"""
AnnotateLayerPropertiesCollection

PARTIAL INTERPRETATION

"""

from ..object import Object
from ..stream import Stream


class AnnotateLayerPropertiesCollection(Object):
    """
    AnnotateLayerPropertiesCollection
    """

    @staticmethod
    def cls_id():
        return '1d5849f3-0d33-11d2-a26f-080009b6f22b'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.properties = []

    @staticmethod
    def compatible_versions():
        return [1, 2]

    def read(self, stream: Stream, version):
        count = stream.read_uint('properties count')
        for i in range(count):
            self.properties.append(stream.read_object('property {}'.format(i + 1)))
            if version > 1:
                stream.read_int('unknown')  # expected=(0, 1, 2, 3, 4, 70, 71, 72)
        if version > 1:
            stream.read_ushort(
                'unknown')  # , expected=count) seems related to numbers in LabelEngineLayerProperties symbol layers
            stream.read_ushort('unknown', expected=0)

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'properties': [p.to_dict() for p in self.properties]
        }
