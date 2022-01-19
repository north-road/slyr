#!/usr/bin/env python
"""
Serializable object subclass
"""

from .feature_layer import FeatureLayer
from ..stream import Stream


class DimensionLayer(FeatureLayer):
    """
    DimensionLayer
    """

    @staticmethod
    def cls_id():
        return 'f1e27e32-0ca7-11d4-80d7-00c04f601565'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    @staticmethod
    def compatible_versions():
        return [4]

    def read(self, stream: Stream, version):
        layer_version_number = stream.read_ushort('layer version number')
        super().read(stream, layer_version_number)

        stream.read_int('unknown', expected=3)

    def to_dict(self):  # pylint: disable=method-hidden
        res = super().to_dict()
        return res
