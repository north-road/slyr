#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class SelectionEnvironment(Object):
    """
    SelectionEnvironment
    """

    @staticmethod
    def cls_id():
        return "e3875b71-d9f5-11d1-add4-080009ec732a"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.point_selection_method = 0
        self.point_search_distance = 0
        self.linear_search_distance = 0
        self.linear_selection_method = 0
        self.area_search_distance = 0
        self.area_selection_method = 0
        self.combination_method = 0
        self.search_tolerance = 0
        self.default_color = None
        self.show_selection_warning = False
        self.warning_threshold = 2000
        self.save_selections = False
        self.clear_invisible_layers = True
        self.scale_selection_symbols = False

    @staticmethod
    def compatible_versions():
        return [4, 5]

    def read(self, stream: Stream, version):
        self.point_selection_method = stream.read_int("point selection method")
        self.point_search_distance = stream.read_double("point search distance")
        self.linear_selection_method = stream.read_int("linear selection method")
        self.linear_search_distance = stream.read_double("linear search distance")
        self.area_selection_method = stream.read_int("area selection method")
        self.area_search_distance = stream.read_double("area search distance")
        self.combination_method = stream.read_int("combination method")
        self.search_tolerance = stream.read_int("search tolerance")

        self.default_color = stream.read_object("default color")
        self.show_selection_warning = stream.read_ushort("show selection warning") != 0
        self.warning_threshold = stream.read_int("warning threshold")
        self.save_selections = stream.read_ushort("save selections") != 0
        self.clear_invisible_layers = stream.read_ushort("clear invisible layers") != 0

        if version > 4:
            self.scale_selection_symbols = (
                stream.read_ushort("scale selection symbols") != 0
            )

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "point_selection_method": self.point_selection_method,
            "point_search_distance": self.point_search_distance,
            "linear_search_distance": self.linear_search_distance,
            "linear_selection_method": self.linear_selection_method,
            "area_search_distance": self.area_search_distance,
            "area_selection_method": self.area_selection_method,
            "combination_method": self.combination_method,
            "search_tolerance": self.search_tolerance,
            "default_color": self.default_color.to_dict()
            if self.default_color
            else None,
            "show_selection_warning": self.show_selection_warning,
            "warning_threshold": self.warning_threshold,
            "save_selections": self.save_selections,
            "clear_invisible_layers": self.clear_invisible_layers,
            "scale_selection_symbols": self.scale_selection_symbols,
        }
