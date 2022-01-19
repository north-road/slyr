#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream
from ..exceptions import RequiresLicenseException


class RasterBasemapLayer(Object):
    """
    RasterBasemapLayer
    """

    @staticmethod
    def cls_id():
        return '57520261-2608-430b-904e-7b0d48c578d5'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    @staticmethod
    def compatible_versions():
        return [5]

    def read(self, stream: Stream, version):
        raise RequiresLicenseException('Converting raster base map layers requires the licensed version of SLYR')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
        }
