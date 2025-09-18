#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class RasterBasemapLayer(Object):
    """
    RasterBasemapLayer
    """

    @staticmethod
    def cls_id():
        return "57520261-2608-430b-904e-7b0d48c578d5"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.crs = None
        self.shader_array = None
        self.raster_layer = None
        self.name = ""
        self.visible = True

    @staticmethod
    def compatible_versions():
        return [5]

    def read(self, stream: Stream, version):
        stream.read_ushort("unknown", expected=0)

        stream.read_raw_clsid(
            "unknown",
            expected=(
                "3e936175-7f9f-4dc6-b5de-930bd66afc47",
                "fc0882fb-10c7-4cba-b0ad-a830d888329a",
            ),
        )  # ??

        self.crs = stream.read_object("crs")
        self.shader_array = stream.read_object("shader array")

        # maybe in RasterShader
        stream.read_double("unknown", expected=1.2028222845998051)
        stream.read_int("unknown", expected=0)

        size = stream.read_int("size")
        stream.read_int("unknown", expected=0)
        start = stream.tell()
        self.raster_layer = stream.read_object("raster layer")
        assert stream.tell() == start + size, (size, stream.tell() - start)

        # copy some stuff from the layer
        if self.raster_layer:
            self.visible = self.raster_layer.visible
            self.name = self.raster_layer.name

        stream.read_string("unknown", expected="")
        stream.read_int("unknown", expected=16)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "crs": self.crs.to_dict() if self.crs else None,
            "shader_array": self.shader_array.to_dict() if self.shader_array else None,
            "raster_layer": self.raster_layer.to_dict() if self.raster_layer else None,
        }
