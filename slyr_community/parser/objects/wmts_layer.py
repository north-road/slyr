#!/usr/bin/env python
"""
Serializable object subclass
"""

from ...parser.object import Object
from ...parser.stream import Stream
from ...parser.exceptions import UnknownClsidException, NotImplementedException


class WmtsLayer(Object):
    """
    WmtsLayer
    """

    @staticmethod
    def cls_id():
        return "61c743a1-8317-416a-8317-10964dadc6ad"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.name = ""
        self.extensions = []
        self.visible = True
        self.show_tips = False
        self.cached = False
        self.zoom_max = 0
        self.zoom_min = 0
        self.transparency = 0
        self.brightness = 0
        self.contrast = 0
        self.weight = 0
        self.provider = None
        self.description = ""

    def read(self, stream: Stream, version):
        stream.read_ushort("unknown", expected=2)

        self.name = stream.read_string("name")

        stream.read_string("unknown")

        self.visible = stream.read_ushort("visible") != 0
        self.show_tips = stream.read_ushort("show tips") != 0
        self.cached = stream.read_ushort("cached") != 0

        self.zoom_max = stream.read_double("zoom max")
        self.zoom_min = stream.read_double("zoom min")

        self.transparency = stream.read_ushort("transparency")
        self.brightness = stream.read_ushort("brightness")
        self.contrast = stream.read_ushort("contrast")

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

        stream.read_int("unknown", expected=1)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        self.weight = stream.read_double("weight")
        self.provider = stream.read_object("provider")

        stream.read_ushort("unknown", expected=(0, 65535))
        stream.read_ushort("unknown", expected=(0, 65535))

        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)

        self.description = stream.read_string("description")
        stream.read_string("unknown")

        stream.read_int("unknown", expected=0)
        stream.read_ushort("unknown", expected=0)

        stream.read_uchar("unknown", expected=1)

        stream.read_object("provider again?")

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "name": self.name,
            "extensions": [e.to_dict() for e in self.extensions],
            "visible": self.visible,
            "show_tips": self.show_tips,
            "cached": self.cached,
            "zoom_max": self.zoom_max,
            "zoom_min": self.zoom_min,
            "transparency": self.transparency,
            "brightness": self.brightness,
            "contrast": self.contrast,
            "weight": self.weight,
            "provider": self.provider.to_dict() if self.provider else None,
            "description": self.description,
        }
