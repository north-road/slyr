#!/usr/bin/env python
"""
Serializable object subclass

NEAR COMPLETE INTERPRETATION - all useful components
"""

from ..object import Object
from ..stream import Stream
from ..exceptions import RequiresLicenseException


class LasDatasetLayer(Object):
    """
    LasDatasetLayer
    """

    @staticmethod
    def cls_id():
        return '431ef9c2-4ac6-4299-b18f-5371fa1a6aa8'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    @staticmethod
    def compatible_versions():
        return [3, 4]

    def read(self, stream: Stream, version):
        raise RequiresLicenseException('Converting point cloud layers requires the licensed version of SLYR')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
        }
