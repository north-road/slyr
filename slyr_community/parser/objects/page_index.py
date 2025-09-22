#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class PageIndex(Object):
    """
    PageIndex
    """

    @staticmethod
    def cls_id():
        return "9384b302-16e4-4f27-a6a8-8c0c99f12579"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.map_frame = None
        self.feature_layer = None
        self.name_field = ""
        self.sort_field = ""
        self.sort_ascending = True
        self.page_number_field = ""
        self.rotation_field = ""
        self.crs_field = ""
        self.round_scale_to_nearest = 0
        self.scale_type = 0
        self.best_fit_size = 0
        self.best_fit_units = 0
        self.start_page_number = 0
        self.current_feature_number = 0
        self.scale_field = ""

    @staticmethod
    def compatible_versions():
        return [2]

    def read(self, stream: Stream, version):
        self.map_frame = stream.read_object("map frame")
        self.feature_layer = stream.read_object("feature layer", expect_existing=True)

        stream.read_int("unknown", expected=6)

        self.name_field = stream.read_string("name field")
        self.sort_field = stream.read_string("sort field")
        self.page_number_field = stream.read_string("page number field")
        self.rotation_field = stream.read_string("rotation field")

        self.scale_field = stream.read_string("scale field")

        self.crs_field = stream.read_string("crs field")
        self.current_feature_number = stream.read_int("current feature number")
        self.sort_ascending = stream.read_ushort("sort ascending") != 0

        stream.read_ushort("unknown", expected=0)

        self.round_scale_to_nearest = stream.read_double("round scale to nearest")
        self.scale_type = stream.read_int(
            "scale type", expected=(0, 1, 2)
        )  # scale value = 0, maintain scale = 1, scale from field = 2
        self.best_fit_size = stream.read_double(
            "best fit size"
        )  # also margin!, e.g. margin 178% = 1.78
        self.best_fit_units = stream.read_int(
            "best fit units"
        )  # 0 = percent, 11 = map units, 1 = page units

        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)

        self.start_page_number = stream.read_int("start page number")

        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=(0, 1, 2))

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "map_frame": self.map_frame,
            "feature_layer": self.feature_layer,
            "name_field": self.name_field,
            "scale_field": self.scale_field,
            "sort_field": self.sort_field,
            "sort_ascending": self.sort_ascending,
            "page_number_field": self.page_number_field,
            "rotation_field": self.rotation_field,
            "crs_field": self.crs_field,
            "round_scale_to_nearest": self.round_scale_to_nearest,
            "scale_type": self.scale_type,
            "best_fit_size": self.best_fit_size,
            "best_fit_units": self.best_fit_units,
            "start_page_number": self.start_page_number,
            "current_feature_number": self.current_feature_number,
        }
