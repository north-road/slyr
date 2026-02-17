#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream
from ..exceptions import UnknownClsidException, NotImplementedException


class MapServerLayer(Object):
    """
    MapServerLayer
    """

    CACHE_KEEP_BETWEEN_SESSIONS = 0
    CACHE_CLEAR_WHEN_SESSION_ENDS = 1
    CACHE_NO = 2

    @staticmethod
    def cls_id():
        return "34d94bb0-3628-4d65-b7ff-4945122f30d5"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.name = ""
        self.path = ""
        self.map_name = ""
        self.description = ""
        self.visible = True
        self.dataset_name = None
        self.children = []
        self.extensions = []
        self.background_color = None

        self.zoom_max = 0
        self.zoom_min = 0

        # used when a zoom range has been set previously, but is currently disabled
        self.stored_zoom_max = 0
        self.stored_zoom_min = 0

        self.transparency = 0

        self.cache_behaviour = MapServerLayer.CACHE_KEEP_BETWEEN_SESSIONS

    @staticmethod
    def cache_method_to_string(method):
        if method == MapServerLayer.CACHE_KEEP_BETWEEN_SESSIONS:
            return "keep_between_sessions"
        elif method == MapServerLayer.CACHE_CLEAR_WHEN_SESSION_ENDS:
            return "clear_when_session_ends"
        elif method == MapServerLayer.CACHE_NO:
            return "no_cache"
        return None

    @staticmethod
    def compatible_versions():
        return [6, 10, 13, 14]

    def read(self, stream: Stream, version):
        self.name = stream.read_string("name")
        stream.read_string("unknown", expected="")
        self.map_name = stream.read_string("map name")

        self.dataset_name = stream.read_object("dataset name")

        self.visible = stream.read_ushort("visible") != 0
        stream.read_ushort("unknown flag", expected=65535)
        stream.read_ushort("unknown")

        self.zoom_max = stream.read_double("zoom max")
        self.zoom_min = stream.read_double("zoom min")

        stream.read_double("unknown (200)", expected=200)
        self.transparency = stream.read_int("transparency")
        stream.read_int("unknown", expected=0)

        count = stream.read_int("sub layer count")
        for i in range(count):
            self.children.append(stream.read_object("sub layer {}".format(i)))

        self.background_color = stream.read_object("background color")

        stream.read_ushort("unknown flag", expected=(0, 65535))
        self.description = stream.read_string("description")

        self.stored_zoom_max = stream.read_double("stored zoom max")
        self.stored_zoom_min = stream.read_double("stored zoom min")

        remote_count = stream.read_int("remote object count")
        for i in range(remote_count):
            size = stream.read_int("size {}".format(i)) + 20  # 20 = object header size
            pos = stream.tell()
            stream.read_int("unknown", expected=0)
            try:
                obj = stream.read_object("remote object", allow_reference=False)
                self.extensions.append(obj)
                assert stream.tell() == pos + size, (size, stream.tell() - pos)
            except (NotImplementedException, UnknownClsidException):
                # don't know this object
                stream.read(size - 20)
            # NOTE - ServerLayerExtension includes layer copyright text

        stream.read_int("unknown", expected=0)
        if version > 6:
            stream.read_ushort("unknown", expected=0)
            stream.read_int("unknown", expected=1)
            self.cache_behaviour = stream.read_int("cache behaviour")
            stream.read_uchar("unknown", expected=1)

        if version > 10:
            stream.read_object("unknown color")
            stream.read_int("unknown", expected=(1, 5, 13))
            stream.read_ushort("unknown flag", expected=(0, 65535))
            stream.read_double("unknown", expected=(1, 2))
            stream.read_ushort("unknown", expected=(0, 4))
            stream.read_ushort("unknown", expected=0)
        if version > 13:
            stream.read_ushort("unknown", expected=0)

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "name": self.name,
            "map_name": self.map_name,
            "description": self.description,
            "dataset_name": self.dataset_name.to_dict() if self.dataset_name else None,
            "visible": self.visible,
            "zoom_min": self.zoom_min,
            "zoom_max": self.zoom_max,
            "stored_zoom_min": self.stored_zoom_min,
            "stored_zoom_max": self.stored_zoom_max,
            "transparency": self.transparency,
            "cache_behaviour": MapServerLayer.cache_method_to_string(
                self.cache_behaviour
            ),
            "children": [c.to_dict() for c in self.children],
            "extensions": [c.to_dict() for c in self.extensions],
            "background_color": self.background_color.to_dict()
            if self.background_color
            else None,
        }


class MapServerBasicSublayer(Object):
    """
    MapServerBasicSublayer
    """

    @staticmethod
    def cls_id():
        return "2fea41b6-d3ef-41ac-b037-622df3c1388d"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.index = 0
        self.name = ""
        self.extensions = []
        self.legend_groups = []
        self.description = ""
        self.sublayers = []

    @staticmethod
    def compatible_versions():
        return [8, 11]

    def read(self, stream: Stream, version):
        self.index = stream.read_int("layer index")
        self.name = stream.read_string("name")

        stream.read_ushort("unknown flag (visibility?)", expected=65535)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=(0, 1092519040))
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_ushort("unknown", expected=0)
        stream.read_ushort("unknown", expected=(0, 65535))

        count = stream.read_int("sub layer count")
        for i in range(count):
            self.sublayers.append(stream.read_object("sublayer {}".format(i + 1)))

        count = stream.read_int("legend group count")
        for i in range(count):
            self.legend_groups.append(
                stream.read_object("legend group {}".format(i + 1))
            )

        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)

        stream.read_object("envelope 1")
        stream.read_object("envelope 2")

        stream.read_ushort("unknown flag", expected=65535)

        self.description = stream.read_string("description or credits")
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)

        stream.read_string("unknown", expected="")
        stream.read_string("unknown layer name?")
        stream.read_string("unknown", expected="")
        stream.read_int("unknown", expected=0)

        stream.read_ushort("unknown flag")

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
            # NOTE - ServerLayerExtension includes layer copyright text

        if version > 8:
            stream.read_int("unknown", expected=0)
            stream.read_ushort("unknown flag")
            stream.read_ushort("unknown", expected=0)
            stream.read_int("unknown", expected=0)
            stream.read_ushort("unknown", expected=0)
            stream.read_int("unknown", expected=(0, 8))

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "index": self.index,
            "name": self.name,
            "extensions": [e.to_dict() for e in self.extensions],
            "legend_groups": [l.to_dict() for l in self.legend_groups],
            "sublayers": [l.to_dict() for l in self.sublayers],
            "description": self.description,
        }


class MapServerSubLayer(Object):
    """
    MapServerSubLayer
    """

    @staticmethod
    def cls_id():
        return "fc69b23b-9959-4dc8-ae26-3ba6f6386498"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.index = 0
        self.name = ""
        self.visible = True
        self.extensions = []
        self.children = []
        self.legend_groups = []
        self.description = ""

    @staticmethod
    def compatible_versions():
        return [8, 11]

    def read(self, stream: Stream, version):
        self.index = stream.read_int("layer index")
        self.name = stream.read_string("name")
        self.visible = stream.read_ushort("visible") != 0

        # suspect the large numbers below are unix epoch dates
        stream.read_int("unknown", expected=0)
        stream.read_int(
            "unknown"
        )  # , expected=(0, 1092519040, 1089701888, 1079672832, 1080721408, 1081774080, 1082822656))
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown")  # , expected=(0, 1079672832, 1080721408))
        stream.read_int("unknown")  # , expected=(0, 4294967295))
        stream.read_ushort("unknown", expected=(0, 65535))
        stream.read_ushort("unknown", expected=(0, 65535))

        child_count = stream.read_int("child count")
        for i in range(child_count):
            self.children.append(stream.read_object("child {}".format(i + 1)))

        count = stream.read_int("legend group count")
        for i in range(count):
            self.legend_groups.append(
                stream.read_object("legend group {}".format(i + 1))
            )

        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)

        stream.read_object("envelope 1")
        stream.read_object("envelope 2")

        stream.read_ushort("unknown flag", expected=(0, 65535))

        self.description = stream.read_string("description or credits")
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)

        # looks like a sql filter
        stream.read_string("filter?")

        stream.read_string("unknown layer name?")
        stream.read_string("unknown", expected="")
        stream.read_int("unknown", expected=0)

        stream.read_ushort("unknown flag")

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
            # NOTE - ServerLayerExtension includes layer copyright text

        if version > 8:
            stream.read_int("unknown", expected=(0, 1))
            stream.read_ushort("unknown flag")
            stream.read_ushort("unknown", expected=0)
            stream.read_int("unknown", expected=0)
            stream.read_ushort("unknown", expected=0)
            stream.read_int("unknown", expected=8)

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "index": self.index,
            "name": self.name,
            "visible": self.visible,
            "extensions": [e.to_dict() for e in self.extensions],
            # 'legend_groups': [l.to_dict() for l in self.legend_groups],
            "description": self.description,
            "children": [c.to_dict() for c in self.children],
        }
