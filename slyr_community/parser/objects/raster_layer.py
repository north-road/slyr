#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..exceptions import RequiresLicenseException
from ..object import Object
from ..stream import Stream


class RasterLayer(Object):
    """
    RasterLayer
    """

    @staticmethod
    def cls_id():
        return 'd02371c9-35f7-11d2-b1f2-00c04f8edeff'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    @staticmethod
    def compatible_versions():
        return [2, 7, 11, 12, 13, 16, 17, 18]

    def read(self, stream: Stream, version):
        raise RequiresLicenseException('Converting raster layers requires the licensed version of SLYR')

    def to_dict(self):  # pylint: disable=method-hidden
        return {}
