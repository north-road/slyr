#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream
from ..exceptions import RequiresLicenseException


class FDOGraphicsLayer(Object):
    """
    FDOGraphicsLayer
    """

    @staticmethod
    def cls_id():
        return "34b2ef83-f4ac-11d1-a245-080009b6f22b"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    @staticmethod
    def compatible_versions():
        return [11]

    def read(self, stream: Stream, version):
        raise RequiresLicenseException(
            "Converting FDO graphics layers requires the licensed version of SLYR"
        )

    def to_dict(self):  # pylint: disable=method-hidden
        return {}
