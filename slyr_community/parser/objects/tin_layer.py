#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream
from ..exceptions import RequiresLicenseException


class TinLayer(Object):
    """
    TinLayer
    """

    @staticmethod
    def cls_id():
        return "fe308f38-bdca-11d1-a523-0000f8774f0f"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    @staticmethod
    def compatible_versions():
        return [7, 8, 10, 11, 12]

    def read(self, stream: Stream, version):
        raise RequiresLicenseException(
            "Converting TIN layers requires the licensed version of SLYR"
        )

    def to_dict(self):  # pylint: disable=method-hidden
        return {}
