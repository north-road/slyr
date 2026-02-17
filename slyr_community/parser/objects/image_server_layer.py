#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object, partially_implemented
from ..stream import Stream


class ImageServerLayer(Object):
    """
    ImageServerLayer
    """

    @staticmethod
    def cls_id():
        return "477d13e7-8d68-45b6-a7fd-2ef442bcce95"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.name = ""
        self.envelope = None
        self.crs = None
        self.dataset_name = None
        self.renderer = None
        self.extensions = []
        self.fields = None
        self.compression_method = ""
        self.compression_quality = 80
        self.rendering_rule = None
        self.mosaic_rule = None
        self.visible = True
        self.zoom_max = 0
        self.zoom_min = 0

        # used when a zoom range has been set previously, but is currently disabled
        self.stored_zoom_max = 0
        self.stored_zoom_min = 0

        self.allow_interactive_effects = False

        self.show_footprints = False
        self.footprint_symbol = None

        self.display_resolution_in_toc = False
        self.display_footprints_for_primary_rasters_only = True

        self.transparency = 0
        self.brightness = 0
        self.contrast = 0

        self.definition_query = ""

        self.selection_color = None
        self.use_selection_symbol = False
        self.selection_symbol = None

        self.enable_time = False

    @staticmethod
    def compatible_versions():
        return [3]

    def read(self, stream: Stream, version):
        internal_version = stream.read_int(
            "internal version", expected=(13, 18, 22, 23)
        )

        stream.read_ushort(expected=8)
        stream.read_stringv2("unknown", expected="")

        stream.read_ushort(expected=8)
        self.name = stream.read_stringv2("name")

        stream.read_ushort(expected=11)
        stream.read_ushort("unknown", expected=65535)

        stream.read_ushort(expected=11)
        stream.read_ushort("unknown", expected=0)

        stream.read_ushort(expected=11)
        self.visible = stream.read_ushort("visible") != 0

        stream.read_ushort(expected=11)
        stream.read_ushort("unknown", expected=0)

        stream.read_ushort(expected=5)
        self.zoom_max = stream.read_double("zoom max")

        stream.read_ushort(expected=5)
        self.zoom_min = stream.read_double("zoom min")

        stream.read_ushort(expected=5)
        stream.read_double("unknown", expected=200)

        stream.read_ushort(expected=8)
        stream.read_stringv2("name again?")

        stream.read_ushort(expected=5)
        self.stored_zoom_max = stream.read_double("stored zoom max")

        stream.read_ushort(expected=5)
        self.stored_zoom_min = stream.read_double("stored zoom min")

        stream.read_ushort(expected=11)
        self.allow_interactive_effects = (
            stream.read_ushort("allow interactive effects") != 0
        )

        stream.read_ushort(expected=11)
        stream.read_ushort("unknown", expected=65535)

        stream.read_ushort(expected=2)
        self.transparency = stream.read_ushort("transparency")

        stream.read_ushort(expected=11)
        stream.read_ushort("unknown", expected=65535)

        stream.read_ushort(expected=2)
        self.brightness = stream.read_ushort("brightness")

        stream.read_ushort(expected=11)
        stream.read_ushort("unknown", expected=65535)

        stream.read_ushort(expected=2)
        self.contrast = stream.read_ushort("contrast")

        stream.read_ushort(expected=2)
        count = stream.read_ushort("unknown count")
        for i in range(count):
            stream.read_ushort("unknown", expected=13)
            self.extensions.append(stream.read_object("extension {}".format(i + 1)))

        stream.read_ushort(expected=13)
        self.envelope = stream.read_object("envelope")

        stream.read_ushort(expected=13)
        assert stream.read_object("unknown") is None

        stream.read_ushort(expected=13)
        self.crs = stream.read_object("crs")

        stream.read_ushort(expected=8)
        stream.read_stringv2("xml definition")

        stream.read_ushort(expected=8)
        stream.read_stringv2("unknown file path")

        stream.read_ushort(expected=13)
        self.dataset_name = stream.read_object("dataset name")

        stream.read_ushort(expected=13)
        self.renderer = stream.read_object("renderer")

        stream.read_ushort(expected=13)
        stream.read_object("envelope?")

        stream.read_ushort(expected=8)
        self.compression_method = stream.read_stringv2("compression method")

        stream.read_ushort(expected=3)
        self.compression_quality = stream.read_int("compression quality")

        stream.read_ushort(expected=11)
        self.display_resolution_in_toc = (
            stream.read_ushort("display resolution in toc") != 0
        )

        stream.read_ushort(expected=8)
        stream.read_stringv2("unknown")

        stream.read_ushort(expected=8)
        stream.read_stringv2("unknown")

        stream.read_ushort(expected=3)
        stream.read_int("unknown", expected=0)

        stream.read_ushort(expected=11)
        stream.read_ushort("unknown", expected=0)

        if internal_version > 13:
            stream.read_ushort(expected=13)
            self.fields = stream.read_object("fields")

            stream.read_ushort(expected=3)
            count = stream.read_int("count")
            for i in range(count):
                stream.read_ushort("unknown", expected=13)
                stream.read_object("field info {}".format(i + 1))

            stream.read_ushort(expected=8)
            self.definition_query = stream.read_stringv2("definition query")

            stream.read_ushort(expected=8)
            stream.read_stringv2("unknown", expected="")

            stream.read_ushort(expected=11)
            stream.read_ushort("unknown", expected=65535)

            stream.read_ushort(expected=3)
            stream.read_int("unknown", expected=0)

            stream.read_ushort(expected=13)
            self.selection_color = stream.read_object("selection color")

            stream.read_ushort(expected=13)
            self.footprint_symbol = stream.read_object("footprint symbol")

            stream.read_ushort(expected=11)
            self.use_selection_symbol = stream.read_ushort("use selection symbol") != 0

            stream.read_ushort(expected=11)
            self.show_footprints = stream.read_ushort("show footprints") != 0

            stream.read_ushort(expected=3)
            self.display_footprints_for_primary_rasters_only = (
                stream.read_int("display footprints for primary rasters only") != 0
            )

            stream.read_ushort(expected=13)
            self.selection_symbol = stream.read_object("selection symbol")

            stream.read_ushort(expected=3)
            stream.read_int("unknown", expected=0)

            stream.read_ushort(expected=11)
            stream.read_ushort("unknown", expected=65535)

            stream.read_ushort(expected=11)
            self.enable_time = stream.read_ushort("enable time") != 0

            stream.read_ushort(expected=13)
            assert stream.read_object("unknown") is None

            stream.read_ushort(expected=8)
            stream.read_stringv2("time field")

            stream.read_ushort(expected=8)
            stream.read_stringv2("unknown", expected="")

            stream.read_ushort(expected=8)
            stream.read_stringv2("unknown", expected=("", "YYYY"))

            stream.read_ushort(expected=8)
            stream.read_stringv2("unknown", expected="")

            stream.read_ushort(expected=13)
            stream.read_object("time extent")

            stream.read_ushort(expected=11)
            stream.read_ushort("unknown", expected=0)

            stream.read_ushort(expected=5)
            stream.read_double("unknown")

            stream.read_ushort(expected=3)
            stream.read_int("unknown", expected=(1, 8, 3224417927))

            stream.read_ushort(expected=5)
            stream.read_double("unknown", expected=0)

            stream.read_ushort(expected=3)
            stream.read_int("unknown", expected=8)

        if internal_version > 18:
            stream.read_ushort(expected=13)
            self.mosaic_rule = stream.read_object("mosaic rule")

            stream.read_ushort(expected=13)
            self.rendering_rule = stream.read_object("rendering rule")

            stream.read_ushort(expected=13)
            assert stream.read_object("unknown") is None

            stream.read_ushort(expected=3)
            count = stream.read_int("band count?")
            for i in range(count):
                stream.read_ushort("unknown", expected=13)
                stream.read_object("band histogram? {}".format(i + 1))

            stream.read_ushort(expected=11)
            stream.read_ushort("unknown", expected=0)

            stream.read_ushort(expected=11)
            stream.read_ushort("unknown", expected=65535)

            stream.read_ushort(expected=3)
            stream.read_int("unknown", expected=0)

        if internal_version > 22:
            stream.read_ushort(expected=13)
            assert stream.read_object("unknown") is None

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "visible": self.visible,
            "zoom_min": self.zoom_min,
            "zoom_max": self.zoom_max,
            "stored_zoom_min": self.stored_zoom_min,
            "stored_zoom_max": self.stored_zoom_max,
            "envelope": self.envelope.to_dict() if self.envelope else None,
            "crs": self.crs.to_dict() if self.crs else None,
            "dataset_name": self.dataset_name.to_dict() if self.dataset_name else None,
            "renderer": self.renderer.to_dict() if self.renderer else None,
            "extensions": [e.to_dict() for e in self.extensions],
            "fields": self.fields.to_dict() if self.fields else None,
            "compression_method": self.compression_method,
            "compression_quality": self.compression_quality,
            "rendering_rule": self.rendering_rule.to_dict()
            if self.rendering_rule
            else None,
            "allow_interactive_effects": self.allow_interactive_effects,
            "show_footprints": self.show_footprints,
            "footprint_symbol": self.footprint_symbol.to_dict()
            if self.footprint_symbol
            else None,
            "display_resolution_in_toc": self.display_resolution_in_toc,
            "display_footprints_for_primary_rasters_only": self.display_footprints_for_primary_rasters_only,
            "transparency": self.transparency,
            "brightness": self.brightness,
            "contrast": self.contrast,
            "mosaic_rule": self.mosaic_rule.to_dict() if self.mosaic_rule else None,
            "definition_query": self.definition_query,
            "selection_color": self.selection_color.to_dict()
            if self.selection_color
            else None,
            "use_selection_symbol": self.use_selection_symbol,
            "selection_symbol": self.selection_symbol.to_dict()
            if self.selection_symbol
            else None,
            "enable_time": self.enable_time,
        }


class UnknownImageServerExtension1(Object):
    """
    UnknownImageServerExtension1
    """

    @staticmethod
    def cls_id():
        return "10e996a7-f3f0-48dd-b0e4-c8920bc8c5c8"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    @staticmethod
    def compatible_versions():
        return [2]

    def read(self, stream: Stream, version):
        stream.read_ushort("unknown", expected=0)
        stream.read_ushort("unknown", expected=65535)
        stream.read_ushort("unknown", expected=65535)
        stream.read_ushort("unknown", expected=65535)
        stream.read_ushort("unknown", expected=65535)

        count = stream.read_int("count")
        for i in range(count):
            stream.read_int("unknown", expected=0)
            size = stream.read_int("unknown", expected=42)
            stream.read(size)

    def to_dict(self):  # pylint: disable=method-hidden
        return {}


@partially_implemented
class UnknownImageServerExtension2(Object):
    """
    UnknownImageServerExtension2
    """

    @staticmethod
    def cls_id():
        return "58583803-fc0b-481d-8fea-cd516ca48fd2"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    @staticmethod
    def compatible_versions():
        return None

    def read(self, stream: Stream, version):
        stream.read(455)

    def to_dict(self):  # pylint: disable=method-hidden
        return {}
