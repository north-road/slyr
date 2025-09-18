#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream
from ..exceptions import RequiresLicenseException


class WmtsLayer(Object):
    """
    WmtsLayer
    """

    @staticmethod
    def cls_id():
        return "61c743a1-8317-416a-8317-10964dadc6ad"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    def read(self, stream: Stream, version):
        raise RequiresLicenseException(
            "Converting WMTS layers requires the licensed version of SLYR"
        )

    def to_dict(self):  # pylint: disable=method-hidden
        return {}
