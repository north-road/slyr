#!/usr/bin/env python
"""
Serializable object subclass
"""

from .element import Element
from ..stream import Stream


class MapFrame(Element):
    """
    MapFrame
    """

    @staticmethod
    def cls_id():
        return "dd94d770-836d-11d0-87ec-080009ec732a"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.map = None
        self.grids = []
        self.locators = []

    @staticmethod
    def compatible_versions():
        return [2, 4]

    def __repr__(self):
        if self.ref_id is not None:
            return "<MapFrame: {} ({})>".format(self.map, self.ref_id)
        else:
            return "<MapFrame: {}>".format(self.map)

    def read(self, stream: Stream, version):
        self.map = stream.read_object("map", expect_existing=True)
        if version >= 4:
            count = stream.read_int("grid count")
            for i in range(count):
                self.grids.append(stream.read_object("grid {}".format(i + 1)))

            count = stream.read_int("locator count")
            for i in range(count):
                self.locators.append(stream.read_object("locator {}".format(i + 1)))
        else:
            extent_type = stream.read_int("maybe extent type??")
            if extent_type in (0, 1, 2):
                stream.read_double("scale")
                stream.read_object("envelope")
            else:
                assert False, extent_type

            count = stream.read_int("grid count")
            for i in range(count):
                self.grids.append(stream.read_object("grid {}".format(i + 1)))

            count = stream.read_int("locator count")
            for i in range(count):
                self.locators.append(stream.read_object("locator {}".format(i + 1)))

        internal_version = stream.read_ushort("internal version", expected=(1, 2))
        stream.read_ushort("unknown", expected=(2, 3))

        self.shape = stream.read_object("shape")
        self.locked = stream.read_int("locked") != 0

        if internal_version > 1:
            self.preserve_aspect = stream.read_ushort("preserve aspect") != 0

        internal_version = stream.read_ushort("internal version", expected=(3, 4, 5, 6))

        self.element_name = stream.read_string("element name")
        self.element_type = stream.read_string("element type")

        variant_type = stream.read_ushort("custom property type")
        if variant_type:
            self.custom_property = stream.read_variant(variant_type, "custom property")

        if internal_version == 3:
            stream.read_int("unknown", expected=0)
            stream.read_int("unknown", expected=0)
            stream.read_int("unknown", expected=0)
            stream.read_ushort("unknown", expected=0)

        self.auto_transform = stream.read_ushort("auto transform") != 0

        if internal_version > 4:
            self.reference_scale = stream.read_double("reference scale")

        if internal_version > 5:
            self.anchor = stream.read_int("anchor")

        self.border = stream.read_object("border")
        self.background = stream.read_object("background")
        self.draft_mode = stream.read_ushort("draft mode") != 0

        if internal_version > 4:
            self.shadow = stream.read_object("shadow")

    def to_dict(self):  # pylint: disable=method-hidden
        res = super().to_dict()
        res["map"] = self.map
        res["grids"] = [g.to_dict() for g in self.grids]
        res["locators"] = [l.to_dict() for l in self.locators]
        return res
