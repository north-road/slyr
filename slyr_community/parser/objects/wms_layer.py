#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream
from ..exceptions import RequiresLicenseException


class WmsMapLayer(Object):
    """
    WmsMapLayer
    """

    @staticmethod
    def cls_id():
        return "e38a56c0-d5bd-4899-b089-c8ed4e38b77f"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    @staticmethod
    def compatible_versions():
        return [2, 3, 6, 7]

    def read(self, stream: Stream, version):
        raise RequiresLicenseException(
            "Converting WMS layers requires the licensed version of SLYR"
        )

    def to_dict(self):  # pylint: disable=method-hidden
        return {}


class WmsGroupLayer(Object):
    """
    WmsGroupLayer
    """

    @staticmethod
    def cls_id():
        return "f677ba62-7ca7-400a-9c59-62930a282ceb"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    @staticmethod
    def compatible_versions():
        return [1]

    def read(self, stream: Stream, version):
        raise RequiresLicenseException(
            "Converting WMS layers requires the licensed version of SLYR"
        )

    def to_dict(self):  # pylint: disable=method-hidden
        return {}


class WmsLayer(Object):
    """
    WmsLayer
    """

    @staticmethod
    def cls_id():
        return "5b0da8f6-5e43-40ae-9871-56ba33936f30"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    @staticmethod
    def compatible_versions():
        return [3, 4, 5]

    def read(self, stream: Stream, version):
        raise RequiresLicenseException(
            "Converting WMS layers requires the licensed version of SLYR"
        )

    def to_dict(self):  # pylint: disable=method-hidden
        return {}
