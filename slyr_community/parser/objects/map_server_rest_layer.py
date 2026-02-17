#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream
from ..exceptions import UnknownClsidException, NotImplementedException


class MapServerRESTLayer(Object):
    """
    MapServerRESTLayer
    """

    @staticmethod
    def cls_id():
        return "1ded52f5-8837-40da-adc3-596c1c4a29ce"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.name = ""
        self.url = ""
        self.extensions = []
        self.sublayers = []
        self.crs = None
        self.properties = None
        self.visible = True
        self.description = ""

    @staticmethod
    def compatible_versions():
        return [7]

    def read(self, stream: Stream, version):
        self.name = stream.read_string("name")
        self.url = stream.read_string("url")

        self.visible = stream.read_ushort("visible") != 0
        stream.read_int("unknown", expected=5)
        stream.read_string("https url?")

        stream.read_string("unknown", expected="")
        stream.read_ascii("json")
        stream.read_string("unknown", expected="")
        stream.read_ascii("json")
        stream.read_string("unknown", expected="")
        stream.read_ascii("json")
        stream.read_string("unknown", expected="")

        size = stream.read_int("size")
        stream.read(size)
        size = stream.read_int("size")
        stream.read(size)
        size = stream.read_int("size")
        stream.read(size)

        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)

        self.properties = stream.read_object("properties")

        stream.read_ushort("unknown", expected=0)
        stream.read_ushort("unknown", expected=65535)
        stream.read_ushort("unknown", expected=0)
        stream.read_int("unknown", expected=0)

        stream.read_int("unknown")  # , expected=1095813344)

        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)

        stream.read_int("unknown", expected=(0, 25))
        stream.read_int("unknown", expected=0)
        stream.read_ushort("unknown")  # , expected=0)

        self.description = stream.read_string("description")

        stream.read_ushort("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_ushort("unknown", expected=0)

        stream.read_int("unknown", expected=(13, 4294967295))
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_ushort("unknown", expected=0)

        count = stream.read_int("sub layer count")
        for i in range(count):
            self.sublayers.append(stream.read_object("sub layer {}".format(i + 1)))

        remote_count = stream.read_int("remote object count")
        for i in range(remote_count):
            size = stream.read_int("size {}".format(i)) + 20  # 20 = object header size
            pos = stream.tell()
            stream.read_int("unknown", expected=0)

            if size == 20:
                stream.read_raw_clsid("Empty object ref")
                continue

            try:
                obj = stream.read_object(
                    "remote object", allow_reference=False, expected_size=size
                )
                self.extensions.append(obj)
                assert stream.tell() == pos + size, (
                    "Expected length {} got length {}".format(size, stream.tell() - pos)
                )
            except UnknownClsidException:
                # don't know this object
                stream.read(size - 20)
            except NotImplementedException:
                # don't know this object
                stream.read(size - 20)

        stream.read_object("extent")

        stream.read_int("tile size?", expected=(2048, 4096))
        stream.read_int("tile size?", expected=(2048, 4096))

        self.crs = stream.read_object("crs")

        stream.read_ushort("unknown")  # , expected=65535)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_object("extent")

        stream.read_ushort("unknown", expected=0)
        stream.read_string("unknown")
        stream.read_string("unknown", expected="")

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "name": self.name,
            "url": self.url,
            "visible": self.visible,
            "extensions": [e.to_dict() for e in self.extensions],
            "sublayers": [l.to_dict() for l in self.sublayers],
            "crs": self.crs.to_dict() if self.crs else None,
            "properties": self.properties.to_dict() if self.properties else None,
        }


class MapServerRESTSubLayer(Object):
    """
    MapServerRESTSubLayer
    """

    @staticmethod
    def cls_id():
        return "8ad8359a-d7f3-4cdb-83e4-fe54ca37ccff"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.extensions = []
        self.name = ""
        self.id = 0
        self.children = []

    @staticmethod
    def compatible_versions():
        return [7]

    def read(self, stream: Stream, version):
        self.id = stream.read_int("layer id")
        stream.read_ushort("unknown", expected=(0, 65535))
        stream.read_object("envelope")

        stream.read_ushort("unknown")  # , expected=(0, 100))
        stream.read_int("unknown", expected=2)
        stream.read_ushort("unknown", expected=0)
        stream.read_ushort("unknown", expected=(0, 112))
        stream.read_ushort("unknown", expected=0)
        stream.read_ushort("unknown")  # , expected=(0, 97))
        stream.read_ushort("unknown")  # , expected=(0, 49))
        stream.read_ushort("unknown")  # , expected=(0, 48))
        stream.read_ushort("unknown")  # , expected=0)
        stream.read_ushort("unknown")  # , expected=(0, 12340, 14128))
        stream.read_ushort("unknown")  # , expected=(0, 42344, 42816, 50368))
        stream.read_ushort("unknown")  # , expected=(0, 19327))

        self.name = stream.read_string("name")
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_object("envelope")

        stream.read_string("unknown")  # , expected='')

        remote_count = stream.read_int("remote object count")
        for i in range(remote_count):
            size = stream.read_int("size {}".format(i)) + 20  # 20 = object header size
            pos = stream.tell()
            stream.read_int("unknown", expected=0)

            if size == 20:
                stream.read_raw_clsid("Empty object ref")
                continue

            try:
                obj = stream.read_object(
                    "remote object", allow_reference=False, expected_size=size
                )
                self.extensions.append(obj)
                assert stream.tell() == pos + size, (
                    "Expected length {} got length {}".format(size, stream.tell() - pos)
                )
            except UnknownClsidException:
                # don't know this object
                stream.read(size - 20)
            except NotImplementedException:
                # don't know this object
                stream.read(size - 20)

            # NOTE - ServerLayerExtension includes layer copyright text
        stream.read_ushort("unknown")

        count = stream.read_int("child count")
        for i in range(count):
            self.children.append(stream.read_object("child {}".format(i + 1)))

        stream.read_ushort("unknown")  # , expected=(0, 74))
        stream.read_ushort("unknown")  # , expected=0)
        stream.read_ushort("unknown")  # , expected=(0, 42352, 42824, 50376))
        stream.read_ushort("unknown")  # , expected=(0, 19327))
        stream.read_ushort("unknown")  # , expected=(0, 11826))
        stream.read_ushort("unknown")  # , expected=(0, 11829))

        stream.read_object("legend groups")

        size = stream.read_int("size")
        stream.read(size)

        stream.read_string("unknown", expected="")
        stream.read_string("unknown")

        stream.read_ushort("unknown", expected=0)
        stream.read_string("unknown", expected="")
        stream.read_int("unknown", expected=0)
        stream.read_ushort("unknown", expected=0)

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "id": self.id,
            "name": self.name,
            "extensions": [e.to_dict() for e in self.extensions],
        }
