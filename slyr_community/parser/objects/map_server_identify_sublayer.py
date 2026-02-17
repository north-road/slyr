#!/usr/bin/env python
"""
Serializable object subclass
"""

from ...parser.object import Object
from ...parser.stream import Stream
from ...parser.exceptions import UnknownClsidException


class MapServerIdentifySublayer(Object):
    """
    MapServerIdentifySublayer
    """

    @staticmethod
    def cls_id():
        return "4289879c-9ce3-43a4-9f13-5ce7fba5ceb7"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.index = 0
        self.name = ""
        self.visible = True
        self.extensions = []
        self.legend_groups = []
        self.children = []

    @staticmethod
    def compatible_versions():
        return [8, 11]

    def read(self, stream: Stream, version):
        self.index = stream.read_int("layer index")
        self.name = stream.read_string("name")
        self.visible = stream.read_ushort("visible") != 0
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=(0, 1091674624))
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_ushort("unknown", expected=(0, 0xFFFF))
        stream.read_ushort("unknown", expected=(0, 0xFFFF))
        child_count = stream.read_int("child count")
        for i in range(child_count):
            self.children.append(stream.read_object("child {}".format(i + 1)))

        legend_count = stream.read_int("legend count")
        for i in range(legend_count):
            self.legend_groups.append(
                stream.read_object("legend group {}".format(i + 1))
            )

        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)

        stream.read_object("unknown envelope 1")
        stream.read_object("unknown envelope 2")

        stream.read_ushort("unknown", expected=(0, 65535))

        stream.read_string("description?")

        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)

        stream.read_string("unknown", expected="")
        stream.read_string("unknown", expected="")
        stream.read_string("unknown", expected="")

        stream.read_ushort("unknown", expected=0)
        stream.read_ushort("unknown", expected=(0, 0xFFFF))
        stream.read_ushort("unknown", expected=(0, 0xFFFF))

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
            stream.read_int("unknown", expected=0)
            stream.read_int("unknown", expected=0)
            stream.read_ushort("unknown", expected=0)
            stream.read_int("unknown", expected=(0, 8))

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "index": self.index,
            "name": self.name,
            "visible": self.visible,
            "extensions": [e.to_dict() for e in self.extensions],
            "legend_groups": [g.to_dict() for g in self.legend_groups],
            "children": [c.to_dict() for c in self.children],
        }
