#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..exceptions import UnknownClsidException, NotImplementedException
from ..object import Object
from ..stream import Stream


class RasterCatalogLayer(Object):
    """
    RasterCatalogLayer
    """

    @staticmethod
    def cls_id():
        return "1493c960-f620-11d3-8d6c-00c04f5b87b2"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.extensions = []
        self.renderer = None
        self.display_rasters = 0
        self.crs = None
        self.resampling_type = 0
        self.use_scale = False
        self.transition_scale = 0
        self.redraw_display = False
        self.delay_draw = 0
        self.draw_rasters_only = False
        self.visible = True
        self.name = ""
        self.dataset_name = None
        self.show_tips = False
        self.relative_base = ""
        self.cached = False
        self.zoom_max = 0
        self.zoom_min = 0
        self.primary_field = 0
        self.symbol = None
        self.transparency = 0
        self.contrast = 0
        self.brightness = 0
        self.renderer = None

    @staticmethod
    def compatible_versions():
        return None

    # pylint: disable=too-many-statements
    def read(self, stream: Stream, version):
        remote_count = stream.read_int("remote object count")
        for i in range(remote_count):
            size = stream.read_int("size {}".format(i)) + 4
            pos = stream.tell()
            stream.read_int("unknown", expected=0)
            try:
                obj = stream.read_object(
                    "remote object", allow_reference=True, expected_size=size
                )
                self.extensions.append(obj)
                assert stream.tell() == pos + size, (
                    "Expected length {} got length {}".format(size, stream.tell() - pos)
                )
            except UnknownClsidException:
                # don't know this object
                stream.read(size - 16)
            except NotImplementedException:
                # don't know this object
                stream.read(size - 16)

        # pylint: disable=too-many-branches
        def handler(ref, size):
            if ref == 1:
                assert size == 0xFFFFFFFF
                self.dataset_name = stream.read_object(
                    "dataset name", allow_reference=False
                )
            elif ref == 2:
                self.name = stream.read_string("name", size=size)
            elif ref == 3:
                self.relative_base = stream.read_string("relative base", size=size)
            elif ref == 4:
                assert size == 2
                self.visible = stream.read_ushort("visible") != 0
            elif ref == 5:
                assert size == 2
                self.show_tips = stream.read_ushort("show tips") != 0
            elif ref == 6:
                assert size == 2
                self.cached = stream.read_ushort("cached") != 0
            elif ref == 7:
                assert size == 8
                self.zoom_max = stream.read_double("zoom max")
            elif ref == 8:
                assert size == 8
                self.zoom_min = stream.read_double("zoom min")
            elif ref == 9:
                assert size == 4
                self.display_rasters = stream.read_int("display rasters")
                stream.read_int(expected=9)
                stream.read_int(expected=4)
                self.primary_field = stream.read_int("primary field")
            elif ref == 10:
                assert size == 0xFFFFFFFF
                self.symbol = stream.read_object("symbol", allow_reference=False)
            elif ref == 11:
                assert size == 4
                self.transparency = stream.read_int("transparency")
            elif ref == 12:
                assert size == 2
                self.contrast = stream.read_ushort("contrast")
            elif ref == 13:
                assert size == 2
                self.brightness = stream.read_ushort("brightness")
            elif ref == 14:
                assert size == 2
                stream.read_ushort("unknown", expected=0)
            elif ref == 15:
                assert size == 0xFFFFFFFF
                self.crs = stream.read_object("crs", allow_reference=False)
            elif ref == 16:
                assert size == 4
                stream.read_int("unknown", expected=0)
            elif ref == 17:
                assert size == 0xFFFFFFFF
                stream.read_object("rgb renderer?", allow_reference=False)
            elif ref == 30:
                assert size == 2
                # renderer count?
                stream.read_ushort("unknown", expected=0)
            # elif ref >= 31:
            #    if size == 0xffffffff:
            #        self.renderers.append(stream.read_object('renderer', allow_reference=False))
            #    else:
            #        assert size == 4
            #        stream.read_int(expected=0)
            else:
                assert False, "Unknown property ref {}".format(ref)

        # pylint: enable=too-many-branches

        internal_version = stream.read_int("internal version", expected=(2, 3))
        stream.read_indexed_properties(handler)

        stream.read_ushort("unknown flag", expected=65535)
        stream.read_ushort("unknown flag", expected=65535)

        def handler2(ref, size):
            if ref == 1:
                assert size == 4
                self.resampling_type = stream.read_int("resampling type")
            elif ref == 2:
                assert size == 4
                self.use_scale = stream.read_int("use scale") != 0
            elif ref == 3:
                assert size == 8
                self.transition_scale = stream.read_double("transition scale")
            elif ref == 4:
                assert size == 4
                self.draw_rasters_only = stream.read_int("draw rasters only") != 0
            elif ref == 5:
                assert size == 4
                self.delay_draw = stream.read_int("delay draw")
            elif ref == 6:
                assert size == 4
                stream.read_int("unknown", expected=0)
            else:
                assert False, "Unknown property ref {}".format(ref)

        stream.read_indexed_properties(handler2)

        stream.read_ushort("unknown", expected=65535)
        stream.read_ushort("unknown", expected=65535)
        if internal_version > 2:
            self.renderer = stream.read_object("renderer")

    # pylint: enable=too-many-statements

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "extensions": [e.to_dict() for e in self.extensions],
            "renderer": self.renderer.to_dict() if self.renderer else None,
            "display_rasters": self.display_rasters,
            "crs": self.crs.to_dict() if self.crs else None,
            "resampling_type": self.resampling_type,
            "use_scale": self.use_scale,
            "transition_scale": self.transition_scale,
            "redraw_display": self.redraw_display,
            "delay_draw": self.delay_draw,
            "draw_rasters_only": self.draw_rasters_only,
            "show_tips": self.show_tips,
            "relative_base": self.relative_base,
            "cached": self.cached,
            "zoom_max": self.zoom_max,
            "zoom_min": self.zoom_min,
            "primary_field": self.primary_field,
            "symbol": self.symbol.to_dict() if self.symbol else None,
            "transparency": self.transparency,
            "contrast": self.contrast,
            "brightness": self.brightness,
        }
