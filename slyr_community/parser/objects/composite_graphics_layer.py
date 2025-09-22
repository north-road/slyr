#!/usr/bin/env python
"""
Serializable object subclass

NEAR COMPLETE INTERPRETATION - all useful components
"""

from ..object import Object
from ..stream import Stream


class CompositeGraphicsLayer(Object):
    """
    CompositeGraphicsLayer
    """

    @staticmethod
    def cls_id():
        return "9646bb83-9512-11d2-a2f6-080009b6f22b"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.name = ""
        self.elements = []
        self.annotation_group_crs = None
        self.annotation_groups = []
        self.groups = []
        self.visible = True
        self.show_tips = True
        self.cached = False
        self.zoom_min = 0
        self.zoom_max = 0
        self.barrier_weight = 0
        self.use_associated_layer_visibility = False
        self.overflow_graphics_container = None
        self.associated_layer = None
        self.reference_scale = 0
        self.description = ""

    @staticmethod
    def compatible_versions():
        return [3, 6]

    def read(self, stream: Stream, version):
        count = stream.read_int("element count")
        for i in range(count):
            element_count = stream.read_int("number of elements in {}".format(i + 1))
            elements = []
            for e in range(element_count):
                elements.append(
                    stream.read_object("element {} in {}".format(e + 1, i + 1))
                )
            self.groups.append(elements)

        self.name = stream.read_string("name")
        self.visible = stream.read_ushort("visible") != 0
        self.show_tips = stream.read_ushort("show tips") != 0
        self.cached = stream.read_ushort("cached") != 0
        self.zoom_max = stream.read_double("zoom max")
        self.zoom_min = stream.read_double("zoom min")
        self.barrier_weight = stream.read_int("barrier weight")
        self.use_associated_layer_visibility = (
            stream.read_int("use associated layer visibility") != 0
        )

        stream.read_int("unknown", expected=1)

        self.overflow_graphics_container = stream.read_object("overflow collection")

        self.reference_scale = stream.read_double("reference scale")
        stream.read_int("unknown", expected=1)  # possibly reference scale units?

        count = stream.read_int("annotation group count")
        for i in range(count):
            group = {}
            group["name"] = stream.read_string("annotation group name {}".format(i + 1))
            group["associated_layer"] = stream.read_object("associated layer")

            group["checked"] = (
                stream.read_ushort("checked", expected=(0, 65535)) == 65535
            )
            stream.read_int("unknown", expected=0)

            group["scale_min"] = stream.read_double("scale min")
            group["scale_max"] = stream.read_double("scale max")

            stream.read_int("unknown", expected=3)
            stream.read_int("unknown", expected=(0, 1))

            group["collection"] = stream.read_object("collection")
            group["reference_scale"] = stream.read_double("reference scale")
            self.annotation_groups.append(group)

        stream.read_int("unknown", expected=1)
        self.associated_layer = stream.read_object("associated layer")
        self.annotation_group_crs = stream.read_object("annotation group crs")

        if version >= 6:
            self.description = stream.read_string("description")

            stream.read_int("unknown", expected=0)
            stream.read_int("unknown", expected=0)
            stream.read_int("unknown", expected=0)
            stream.read_int("unknown", expected=0)

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "name": self.name,
            "elements": [e.to_dict() for e in self.elements],
            "groups": [[e.to_dict() for e in g] for g in self.groups],
            "annotation_groups": self.annotation_groups,
            "annotation_group_crs": self.annotation_group_crs.to_dict()
            if self.annotation_group_crs
            else None,
            "visible": self.visible,
            "show_tips": self.show_tips,
            "cached": self.cached,
            "zoom_min": self.zoom_min,
            "zoom_max": self.zoom_max,
            "barrier_weight": self.barrier_weight,
            "use_associated_layer_visibility": self.use_associated_layer_visibility,
            "overflow_graphics_container": self.overflow_graphics_container.to_dict()
            if self.overflow_graphics_container
            else None,
            "associated_layer": self.associated_layer,
            "reference_scale": self.reference_scale,
            "description": self.description,
        }
