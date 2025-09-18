#!/usr/bin/env python
"""
Serializable object subclass
"""

from .element import Element
from ..stream import Stream


class PictureElement(Element):
    """
    PictureElement
    """

    @staticmethod
    def cls_id():
        return "827b9a92-c067-11d2-9f22-00c04f6bc8dd"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.picture = None
        self.picture_path = ""
        self.picture_type = ""
        self.width = 0
        self.height = 0
        self.x = 0
        self.y = 0
        self.picture_field = ""
        self.picture_shows_attachment = False
        self.attachment_filter = ""

    @staticmethod
    def compatible_versions():
        return [2, 4, 5, 9]

    def read(self, stream: Stream, version):
        stream.read_ushort("unknown", expected=2)
        if version > 2:
            stream.read_ushort("unknown", expected=3)

        self.shape = stream.read_object("shape")

        self.locked = stream.read_int("locked") != 0
        if version == 2:
            header_version = stream.read_ushort("header version", expected=(3, 4))
            self.picture_path = stream.read_string("path")
            self.element_type = stream.read_string("type", expected="Picture")
            stream.read_ushort("unknown", expected=0)

            if header_version == 3:
                stream.read_int("unknown", expected=0)
                stream.read_int("unknown", expected=0)
                stream.read_int("unknown", expected=0)
                stream.read_ushort("unknown", expected=0)

            stream.read_ushort("unknown", expected=65535)
            stream.read_ushort("unknown", expected=0)
            stream.read_uchar("unknown", expected=0)
            stream.read_ushort("unknown", expected=65535)
        else:
            self.preserve_aspect = stream.read_ushort("fixed aspect ratio") != 0

            internal_version = stream.read_ushort("internal version", expected=(5, 6))

            self.element_name = stream.read_string("element name")
            self.element_type = stream.read_string(
                "element type", expected=("Picture", "Bild")
            )

            variant_type = stream.read_ushort("custom property type")
            if variant_type:
                self.custom_property = stream.read_variant(
                    variant_type, "custom property"
                )

            self.auto_transform = stream.read_ushort("auto transform") != 0
            self.reference_scale = stream.read_double("reference scale")

            if internal_version > 5:
                self.anchor = stream.read_int("anchor point")

            self.border = stream.read_object("border")
            self.background = stream.read_object("background")
            self.draft_mode = stream.read_ushort("draft mode") != 0
            self.shadow = stream.read_object("shadow")

            is_embedded = stream.read_ushort("is embedded") != 0
            if is_embedded or (version <= 4 and not self.element_name):
                # see eg PLANO PROTECCION AU ALMERIA.mxd
                self.picture = stream.read_object("picture")

        if version > 4:
            self.picture_path = stream.read_string("picture path")
            self.picture_type = stream.read_string("picture type")
            stream.read_string("picture file filter")

        if version > 5:
            self.x = stream.read_double("x")
            self.y = stream.read_double("y")

            # x max/ymax
            self.width = stream.read_double("max x") - self.x
            self.height = stream.read_double("max y") - self.y

            self.picture_field = stream.read_string("picture field")
            self.picture_shows_attachment = (
                stream.read_ushort("picture shows attachment") != 0
            )
            self.attachment_filter = stream.read_string("attachment filter")

            stream.read_string("name again?")  # , expected=('', self.element_name))

    def to_dict(self):  # pylint: disable=method-hidden
        res = super().to_dict()
        res["picture"] = self.picture.to_dict() if self.picture else None
        res["picture_path"] = (self.picture_path,)
        res["picture_type"] = (self.picture_type,)
        res["width"] = self.width
        res["height"] = self.height
        res["x"] = self.x
        res["y"] = self.y
        res["picture_field"] = self.picture_field
        res["picture_shows_attachment"] = self.picture_shows_attachment
        res["attachment_filter"] = self.attachment_filter
        return res
