#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream
from .units import Units


class Page(Object):
    """
    Page
    """

    @staticmethod
    def cls_id():
        return "dd94d76f-836d-11d0-87ec-080009ec732a"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.width = 0
        self.height = 0
        self.left_margin = 0
        self.top_margin = 0
        self.right_margin = 0
        self.bottom_margin = 0
        self.background_color = None
        self.page_size = 0
        self.page_to_printer_mapping = 0
        self.orientation = 1
        self.units = 0
        self.border = None
        self.background = None
        self.printable_area_visible = False
        self.stretch_graphics_with_page = False

    def read(self, stream: Stream, version):
        self.page_size = stream.read_int("page size")  # esriPageFormID
        self.page_to_printer_mapping = stream.read_int("page to printer mapping")  #
        self.orientation = stream.read_ushort(
            "page orientation", expected=(1, 2)
        )  # 1 = portrait
        self.units = stream.read_int("units")

        self.width = stream.read_double("page width")
        self.height = stream.read_double("page height")
        self.left_margin = stream.read_double("left margin")
        self.top_margin = stream.read_double("top margin")
        self.right_margin = stream.read_double("right margin")
        self.bottom_margin = stream.read_double("bottom margin")

        self.printable_area_visible = stream.read_ushort("printable area visible")
        self.stretch_graphics_with_page = (
            stream.read_ushort("stretch graphics with page") != 0
        )

        self.background_color = stream.read_object("background color")

        self.border = stream.read_object("border")
        self.background = stream.read_object("background")

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "width": self.width,
            "height": self.height,
            "left_margin": self.left_margin,
            "top_margin": self.top_margin,
            "right_margin": self.right_margin,
            "bottom_margin": self.bottom_margin,
            "background_color": self.background_color.to_dict()
            if self.background_color
            else None,
            "page_size": self.page_size,
            "page_to_printer_mapping": self.page_to_printer_mapping,
            "orientation": self.orientation,
            "units": Units.distance_unit_to_string(self.units),
            "border": self.border.to_dict() if self.border else None,
            "background": self.background.to_dict() if self.background else None,
            "printable_area_visible": self.printable_area_visible,
            "stretch_graphics_with_page": self.stretch_graphics_with_page,
        }
