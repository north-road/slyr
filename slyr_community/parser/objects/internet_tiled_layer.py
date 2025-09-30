#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream
from ..exceptions import RequiresLicenseException


class InternetTiledLayer(Object):
    """
    InternetTiledLayer
    """

    @staticmethod
    def cls_id():
        return "a4badc1b-ebed-4a29-99dc-c6334de352ad"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    @staticmethod
    def compatible_versions():
        return [2]

    def read(self, stream: Stream, version):
        raise RequiresLicenseException(
            "Converting internet tiled layers requires the licensed version of SLYR"
        )

    def to_dict(self):  # pylint: disable=method-hidden
        return {}


class MSVirtualEarthLayerProvider(Object):
    """
    MSVirtualEarthLayerProvider
    """

    @staticmethod
    def cls_id():
        return "1ce3ac83-26e0-42cd-af4d-213b72ceb864"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    @staticmethod
    def compatible_versions():
        return [1, 2, 4]

    def read(self, stream: Stream, version):
        raise RequiresLicenseException(
            "Converting internet tiled layers requires the licensed version of SLYR"
        )

    def to_dict(self):  # pylint: disable=method-hidden
        return {}


class TileCacheInfo(Object):
    """
    TileCacheInfo
    """

    @staticmethod
    def cls_id():
        return "01312017-7d38-4d2b-91a0-05c548ade7f3"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    @staticmethod
    def compatible_versions():
        return [2, 3]

    def read(self, stream: Stream, version):
        raise RequiresLicenseException(
            "Converting internet tiled layers requires the licensed version of SLYR"
        )

    def to_dict(self):  # pylint: disable=method-hidden
        return {}


class OpenStreetMapProvider(Object):
    """
    OpenStreetMapProvider
    """

    @staticmethod
    def cls_id():
        return "351eeb0c-bcb9-4064-9e61-1219169af633"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    @staticmethod
    def compatible_versions():
        return [1, 2]

    def read(self, stream: Stream, version):
        raise RequiresLicenseException(
            "Converting internet tiled layers requires the licensed version of SLYR"
        )

    def to_dict(self):  # pylint: disable=method-hidden
        return {}
