#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream
from ..exceptions import RequiresLicenseException


class CompositeGraphicsLayer(Object):
    """
    CompositeGraphicsLayer
    """

    @staticmethod
    def cls_id():
        return "9646bb83-9512-11d2-a2f6-080009b6f22b"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    @staticmethod
    def compatible_versions():
        return [3, 6]

    def read(self, stream: Stream, version):
        raise RequiresLicenseException(
            "Converting composite graphics layers requires the licensed version of SLYR"
        )

    def to_dict(self):  # pylint: disable=method-hidden
        return {}
