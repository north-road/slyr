#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream
from ..exceptions import RequiresLicenseException


class MapServerLayer(Object):
    """
    MapServerLayer
    """

    @staticmethod
    def cls_id():
        return "34d94bb0-3628-4d65-b7ff-4945122f30d5"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    @staticmethod
    def compatible_versions():
        return [6, 10, 13, 14]

    def read(self, stream: Stream, version):
        raise RequiresLicenseException(
            "Converting map server layers requires the licensed version of SLYR"
        )

    def to_dict(self):  # pylint: disable=method-hidden
        return {}


class MapServerBasicSublayer(Object):
    """
    MapServerBasicSublayer
    """

    @staticmethod
    def cls_id():
        return "2fea41b6-d3ef-41ac-b037-622df3c1388d"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    @staticmethod
    def compatible_versions():
        return [8, 11]

    def read(self, stream: Stream, version):
        raise RequiresLicenseException(
            "Converting map server layers requires the licensed version of SLYR"
        )

    def to_dict(self):  # pylint: disable=method-hidden
        return {}


class MapServerSubLayer(Object):
    """
    MapServerSubLayer
    """

    @staticmethod
    def cls_id():
        return "fc69b23b-9959-4dc8-ae26-3ba6f6386498"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    @staticmethod
    def compatible_versions():
        return [8, 11]

    def read(self, stream: Stream, version):
        raise RequiresLicenseException(
            "Converting map server layers requires the licensed version of SLYR"
        )

    def to_dict(self):  # pylint: disable=method-hidden
        return {}
