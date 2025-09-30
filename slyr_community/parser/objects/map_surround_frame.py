#!/usr/bin/env python
"""
Serializable object subclass
"""

from .element import Element
from ..stream import Stream


class MapSurroundFrame(Element):
    """
    MapSurroundFrame
    """

    @staticmethod
    def cls_id():
        return "83ffcae1-edca-11d0-8683-0000f8751720"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.element = None
        self.map_frame = None
        self.map_bounds = None

    @staticmethod
    def compatible_versions():
        return [1, 2, 3]

    def read(self, stream: Stream, version):
        self.element = stream.read_object("element", expect_existing=True)
        self.map_frame = stream.read_object("map frame")
        self.map_bounds = stream.read_object("map bounds")

        internal_version1 = stream.read_ushort("internal version 1", expected=(1, 2))
        stream.read_ushort("unknown", expected=(2, 3))
        self.shape = stream.read_object("shape")

        self.locked = stream.read_int("locked") != 0
        if internal_version1 == 1:
            internal_version = stream.read_ushort("internal version", expected=(3, 4))
            self.element_name = stream.read_string("name")
            self.element_type = stream.read_string("type")
            stream.read_ushort("unknown", expected=0)
            if internal_version == 3:
                stream.read_int("unknown", expected=0)
                stream.read_int("unknown", expected=0)
                stream.read_int("unknown", expected=0)
                stream.read_ushort("unknown", expected=0)
                stream.read_ushort("unknown", expected=65535)

            else:
                stream.read_ushort("unknown", expected=65535)
                # stream.read_ushort('unknown', expected=0)
        else:
            self.preserve_aspect = stream.read_ushort("preserve aspect") != 0

            internal_version = stream.read_ushort(
                "internal version", expected=(2, 5, 6)
            )

            self.element_name = stream.read_string("element name")
            self.element_type = stream.read_string("element type")

            variant_type = stream.read_ushort("custom property type")
            if variant_type:
                self.custom_property = stream.read_variant(
                    variant_type, "custom property"
                )

            self.auto_transform = stream.read_ushort("auto transform") != 0
            self.reference_scale = stream.read_double("reference scale")

        if internal_version > 5:
            self.anchor = stream.read_int("anchor")

        self.border = stream.read_object("border")
        self.background = stream.read_object("background")

        if internal_version1 == 1:
            stream.read_ushort("unknown", expected=0)

        if internal_version > 4:
            self.draft_mode = stream.read_ushort("draft mode") != 0
            self.shadow = stream.read_object("shadow")

        # shadow offset?
        if version > 2:
            stream.read_double("unknown")  # , expected=(13, 1.6578999947448116))
            stream.read_double("unknown")  # , expected=(14, 7.940599994744927))

    def to_dict(self):  # pylint: disable=method-hidden
        res = super().to_dict()
        res["element"] = self.element.to_dict() if self.element else None
        res["map_frame"] = self.map_frame.to_dict() if self.map_frame else None
        res["map_bounds"] = self.map_bounds.to_dict() if self.map_bounds else None
        return res
