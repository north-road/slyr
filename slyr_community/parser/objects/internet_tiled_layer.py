#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream
from ..exceptions import UnknownClsidException, NotImplementedException


class InternetTiledLayer(Object):
    """
    InternetTiledLayer
    """

    CACHE_KEEP_BETWEEN_SESSIONS = 0
    CACHE_CLEAR_WHEN_SESSION_ENDS = 1
    CACHE_NO = 2

    @staticmethod
    def cls_id():
        return "a4badc1b-ebed-4a29-99dc-c6334de352ad"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.extensions = []
        self.name = ""
        self.identifier = ""
        self.visible = True
        self.zoom_max = 0
        self.zoom_min = 0

        self.definition = None

        # used when a zoom range has been set previously, but is currently disabled
        self.stored_zoom_max = 0
        self.stored_zoom_min = 0

        self.cache_behaviour = InternetTiledLayer.CACHE_KEEP_BETWEEN_SESSIONS

    @staticmethod
    def cache_method_to_string(method):
        if method == InternetTiledLayer.CACHE_KEEP_BETWEEN_SESSIONS:
            return "keep_between_sessions"
        elif method == InternetTiledLayer.CACHE_CLEAR_WHEN_SESSION_ENDS:
            return "clear_when_session_ends"
        elif method == InternetTiledLayer.CACHE_NO:
            return "no_cache"
        return None

    @staticmethod
    def compatible_versions():
        return [2]

    def read(self, stream: Stream, version):
        self.name = stream.read_string("name")
        self.identifier = stream.read_string("identifier")
        self.visible = stream.read_ushort("visible") != 0

        stream.read_ushort("unknown", expected=65535)

        stream.read_int("unknown", expected=(0, 65535))
        stream.read_ushort("unknown", expected=0)
        stream.read_double("unknown")
        stream.read_double("unknown")
        stream.read_ushort("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)

        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)

        remote_count = stream.read_int("remote object count")
        for i in range(remote_count):
            size = stream.read_int("size {}".format(i)) + 20  # 20 = object header size
            pos = stream.tell()
            stream.read_int("unknown", expected=0)
            try:
                obj = stream.read_object("remote object", allow_reference=False)
                self.extensions.append(obj)
                assert stream.tell() == pos + size, (size, stream.tell() - pos)
            except UnknownClsidException:
                # don't know this object
                stream.read(size - 20)
            except NotImplementedException:
                # don't know this object
                stream.read(size - 20)

            # NOTE - ServerLayerExtension includes layer copyright text

        stream.read_int("unknown", expected=(1, 3))
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)

        stream.read_double("unknown (200)", expected=200)

        self.definition = stream.read_object("definition")

        stream.read_int("unknown", expected=(0, 1, 2))

        self.zoom_max = stream.read_double("zoom max")
        self.zoom_min = stream.read_double("zoom min")

        stream.read_string("description again")
        stream.read_string("attribution again")

        stream.read_ushort("unknown", expected=0)
        self.cache_behaviour = stream.read_int("cache behavior", expected=(0, 1, 2))
        stream.read_uchar("unknown", expected=1)

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "name": self.name,
            "identifier": self.identifier,
            "extensions": [e.to_dict() for e in self.extensions],
            "zoom_max": self.zoom_max,
            "zoom_min": self.zoom_min,
            "cache_behaviour": InternetTiledLayer.cache_method_to_string(
                self.cache_behaviour
            ),
            "definition": self.definition.to_dict() if self.definition else None,
        }


class MSVirtualEarthLayerProvider(Object):
    """
    MSVirtualEarthLayerProvider
    """

    @staticmethod
    def cls_id():
        return "1ce3ac83-26e0-42cd-af4d-213b72ceb864"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.cache_info = None
        self.culture = "en-US"

    @staticmethod
    def compatible_versions():
        return [1, 2, 4]

    def read(self, stream, version):
        stream.read_string("name?")
        stream.read_string("url?")
        stream.read_string("description?")

        stream.read_ushort("unknown", expected=0)
        stream.read_string("copyright?")

        self.cache_info = stream.read_object("cache info")

        if version > 1:
            self.culture = stream.read_string("culture") or "en-US"
        if version > 2:
            stream.read_string("api key?")
            stream.read_string("unknown", expected="")

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "cache_info": self.cache_info.to_dict() if self.cache_info else None,
            "culture": self.culture,
        }


class TileCacheInfo(Object):
    """
    TileCacheInfo
    """

    @staticmethod
    def cls_id():
        return "01312017-7d38-4d2b-91a0-05c548ade7f3"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.crs = None
        self.origin = None
        self.dpi = 96
        self.lod_info = None

    @staticmethod
    def compatible_versions():
        return [2, 3]

    def read(self, stream, version):
        self.origin = stream.read_object("origin")

        stream.read_uchar("unknown", expected=0)
        stream.read_int("unknown", expected=1)
        stream.read_ushort("unknown", expected=1)
        stream.read_uchar("unknown", expected=0)

        self.lod_info = stream.read_object("levels of detail")
        self.crs = stream.read_object("crs")
        if version < 3:
            self.dpi = stream.read_int("dpi", expected=96)
        else:
            self.dpi = stream.read_double("dpi", expected=(96, 90.7142857142743))

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "origin": self.origin.to_dict() if self.origin else None,
            "crs": self.crs.to_dict() if self.crs else None,
            "dpi": self.dpi,
            "lod_info": self.lod_info.to_dict() if self.lod_info else None,
        }


class OpenStreetMapProvider(Object):
    """
    OpenStreetMapProvider

    Note: not just OpenStreetMapProvider, urls containing Google maps
    tiles have been found too!
    """

    @staticmethod
    def cls_id():
        return "351eeb0c-bcb9-4064-9e61-1219169af633"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.cache_info = None

    @staticmethod
    def compatible_versions():
        return [1, 2]

    def read(self, stream, version):
        stream.read_string("name?")
        stream.read_string("url?")
        stream.read_string("description?")

        stream.read_ushort("unknown", expected=65535)
        stream.read_string("copyright?")

        self.cache_info = stream.read_object("cache info")

        if version > 1:
            stream.read_string("tile url again?")

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "cache_info": self.cache_info.to_dict() if self.cache_info else None,
        }
