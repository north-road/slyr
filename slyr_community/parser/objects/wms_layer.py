#!/usr/bin/env python
"""
Serializable object subclass
"""

from ...parser.object import Object
from ...parser.stream import Stream
from ...parser.exceptions import UnknownClsidException


class WmsMapLayer(Object):
    """
    WmsMapLayer
    """

    IMAGE_FORMAT_JPEG = 1
    IMAGE_FORMAT_PNG8 = 4
    IMAGE_FORMAT_PNG24 = 5
    IMAGE_FORMAT_PNG32 = 13

    @staticmethod
    def cls_id():
        return "e38a56c0-d5bd-4899-b089-c8ed4e38b77f"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.name = ""
        self.connection_name = None
        self.extensions = []
        self.zoom_min = 0
        self.zoom_max = 0
        self.transparency = 0
        self.visible = True
        self.background_color = None
        self.transparent_background = True
        self.description = ""
        self.custom_params = None
        self.children = []
        self.image_format = WmsMapLayer.IMAGE_FORMAT_JPEG

    @staticmethod
    def compatible_versions():
        return [2, 3, 6, 7]

    @staticmethod
    def image_format_to_string(image_format):
        if image_format == WmsMapLayer.IMAGE_FORMAT_JPEG:
            return "jpeg"
        elif image_format == WmsMapLayer.IMAGE_FORMAT_PNG8:
            return "png8"
        elif image_format == WmsMapLayer.IMAGE_FORMAT_PNG24:
            return "png24"
        elif image_format == WmsMapLayer.IMAGE_FORMAT_PNG32:
            return "png32"

    def read(self, stream: Stream, version):
        self.connection_name = stream.read_object("connection name")
        self.name = stream.read_string("layer name")
        self.visible = stream.read_ushort("visibility") != 0
        self.transparent_background = stream.read_ushort("transparent background") != 0
        stream.read_ushort("unknown flag")
        stream.read_ushort("unknown flag")

        self.background_color = stream.read_object("background color")
        stream.read_double("unknown", expected=(-1, 200))

        self.transparency = stream.read_int("transparency")
        stream.read_int("unknown", expected=0)
        root_group_count = stream.read_int("root group count")
        for i in range(root_group_count):
            self.children.append(stream.read_object("directory {}".format(i + 1)))

        stream.read_ushort("unknown flag")
        self.description = stream.read_string("description")

        self.zoom_max = stream.read_double("zoom max")
        self.zoom_min = stream.read_double("zoom min")
        stream.read_double("stored zoom max when zoom max not enabled?")
        stream.read_double("stored zoom min when zoom min not enabled?")

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

        if version > 2:
            stream.read_int("unknown", expected=0)
            stream.read_int("unknown", expected=0)
            stream.read_int("unknown", expected=0)
            stream.read_int("unknown", expected=0)
            self.image_format = stream.read_int("format")
            stream.read_ushort("unknown flag")
            stream.read_double("unknown", expected=(0, -1))
            stream.read_int("unknown", expected=(0, 5))
            stream.read_int("unknown", expected=0)
            stream.read_int("unknown", expected=0)
            stream.read_int("unknown", expected=(0, 5))

        if version > 6:
            self.custom_params = stream.read_object("custom params")

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "connection_name": self.connection_name.to_dict()
            if self.connection_name
            else None,
            "name": self.name,
            "zoom_min": self.zoom_min,
            "zoom_max": self.zoom_max,
            "transparency": self.transparency,
            "visible": self.visible,
            "background_color": self.background_color.to_dict()
            if self.background_color
            else None,
            "transparent_background": self.transparent_background,
            "description": self.description,
            "custom_params": self.custom_params.to_dict()
            if self.custom_params
            else None,
            "children": [c.to_dict() for c in self.children],
            "image_format": WmsMapLayer.image_format_to_string(self.image_format),
        }


class WmsGroupLayer(Object):
    """
    WmsGroupLayer
    """

    @staticmethod
    def cls_id():
        return "f677ba62-7ca7-400a-9c59-62930a282ceb"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.visible = True
        self.name = ""
        self.children = []
        self.description = ""

    @staticmethod
    def compatible_versions():
        return [1]

    def read(self, stream: Stream, version):
        self.name = stream.read_string("name")
        self.visible = stream.read_ushort("visibility") != 0
        stream.read_ushort("unknown flag", expected=65535)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_ushort("unknown flag", expected=0)

        count = stream.read_int("child count")
        for i in range(count):
            self.children.append(stream.read_object("child {}".format(i + 1)))

        stream.read_ushort("unknown flag")
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_double("unknown", expected=(-1, 1, 200))

        self.description = stream.read_string("description")
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "visible": self.visible,
            "name": self.name,
            "description": self.description,
            "children": [c.to_dict() for c in self.children],
        }


class WmsLayer(Object):
    """
    WmsLayer
    """

    @staticmethod
    def cls_id():
        return "5b0da8f6-5e43-40ae-9871-56ba33936f30"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.name = ""
        self.id = ""
        self.style = ""
        self.visible = True
        self.show_tips = False
        self.cached = False
        self.description = ""

    @staticmethod
    def compatible_versions():
        return [3, 4, 5]

    def read(self, stream: Stream, version):
        self.name = stream.read_string("layer name?")
        self.id = stream.read_string("layer id?")
        self.visible = stream.read_ushort("visible") != 0
        self.show_tips = stream.read_ushort("show tips") != 0
        self.cached = stream.read_ushort("cached") != 0
        self.description = stream.read_string("description")
        stream.read_ushort("unknown flag", expected=(0, 65535))
        if version > 3:
            self.style = stream.read_string("style")
        if version > 4:
            stream.read_ushort("unknown flag")
            stream.read_double("unknown", expected=(0, -1))
            stream.read_int("image format?", expected=(0, 5))

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "name": self.name,
            "id": self.id,
            "style": self.style,
            "visible": self.visible,
            "show_tips": self.show_tips,
            "cached": self.cached,
            "description": self.description,
        }
