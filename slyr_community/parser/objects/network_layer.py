#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..exceptions import NotImplementedException, UnknownClsidException
from ..object import Object
from ..stream import Stream


class NetworkLayer(Object):
    """
    NetworkLayer
    """

    @staticmethod
    def cls_id():
        return "d4f8e94b-5cf5-4f8f-8b4d-5b25ae4c0af9"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.extensions = []
        self.name = ""
        self.dataset_name = None
        self.crs = None
        self.show_tips = False
        self.cached = False
        self.zoom_max = None
        self.zoom_min = None
        self.visible = False
        self.scale_symbols = False
        self.weight = 0
        self.description = ""

    @staticmethod
    def compatible_versions():
        return None

    def read(self, stream: Stream, version):
        stream.read_ushort("unknown", expected=0)
        self.name = stream.read_string("name")
        self.dataset_name = stream.read_object("dataset name")

        self.crs = stream.read_object("crs")
        stream.read_object("display filter")

        self.show_tips = stream.read_ushort("show tips") != 0
        stream.read_string("unknown", expected="")
        self.cached = stream.read_ushort("cached") != 0

        self.zoom_max = stream.read_double("zoom max")
        self.zoom_min = stream.read_double("zoom min")

        self.visible = stream.read_ushort("visible") != 0
        self.scale_symbols = stream.read_ushort("scale symbols") != 0

        self.weight = stream.read_double("layer weight")

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

        self.description = stream.read_string("description")

        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        count = stream.read_int("count")

        for i in range(count):
            _ = stream.read_ushort("renderer visible {} ".format(i + 1)) != 0
            stream.read_object("renderer {}".format(i + 1))

            stream.read_int("unknown", expected=0)
            stream.read_int("unknown", expected=0)
            stream.read_int("unknown", expected=0)
            stream.read_int("unknown", expected=0)

    def to_dict(self):  # pylint: disable=method-hidden
        return {}
