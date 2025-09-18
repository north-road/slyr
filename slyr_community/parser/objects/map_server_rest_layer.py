#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream
from ..exceptions import RequiresLicenseException


class MapServerRESTLayer(Object):
    """
    MapServerRESTLayer
    """

    @staticmethod
    def cls_id():
        return "1ded52f5-8837-40da-adc3-596c1c4a29ce"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    @staticmethod
    def compatible_versions():
        return [7]

    def read(self, stream: Stream, version):
        raise RequiresLicenseException(
            "Converting MapServer REST layers requires the licensed version of SLYR"
        )

    def to_dict(self):  # pylint: disable=method-hidden
        return {}


class MapServerRESTSubLayer(Object):
    """
    MapServerRESTSubLayer
    """

    @staticmethod
    def cls_id():
        return "8ad8359a-d7f3-4cdb-83e4-fe54ca37ccff"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    @staticmethod
    def compatible_versions():
        return [7]

    def read(self, stream: Stream, version):
        raise RequiresLicenseException(
            "Converting MapServer REST layers requires the licensed version of SLYR"
        )

    def to_dict(self):  # pylint: disable=method-hidden
        return {}
