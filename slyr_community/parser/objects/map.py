#!/usr/bin/env python
"""
Serializable object subclass
"""

from collections import OrderedDict

from ..object import Object
from .group_layer import GroupLayer

from .units import Units
from ..stream import Stream
from ..exceptions import CustomExtensionClsidException


class Map(Object):
    """
    Map
    """

    @staticmethod
    def cls_id():
        return "e6bdaa76-4d35-11d0-98be-00805f7ced21"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.name = ""
        self.description = ""
        self.crs = None
        self.root_groups = []
        self.graphics_layer = None
        self.illumination_properties = None
        self.overposter_properties = None
        self.credits = ""
        self.fixed_extent = None
        self.fixed_scale = 0
        self.rotation = 0
        self.simulate_layer_transparency_in_legends = False
        self.distance_units = Units.DISTANCE_METERS
        self.map_units = Units.DISTANCE_METERS
        self.allow_assignment_of_unique_ids_for_publishing = False
        self.background = None
        self.bookmarks = []
        self.standalone_tables = []
        self.transformations = []
        self.cache_build_when_map_extent_changes = False
        self.cache_minimum_scale = 0
        self.case_use_minimum_scale = False
        self.clipping_border = None
        self.clipping_path = None
        self.clipping_exempt_layers = []
        self.scales = []
        self.elements = []
        self.draw_using_masking_options = False
        self.masking = OrderedDict()
        self.initial_view = None

        self.full_extent_x_min = None
        self.full_extent_y_min = None
        self.full_extent_x_max = None
        self.full_extent_y_max = None

        self.area_of_interest = None

        self.verbose_events = False
        self.reference_scale = 0
        self.use_symbol_levels = True

        self.conserve_memory = False
        self.output_band_size = 0
        self.delay_background_draw = False
        self.expanded = True

        self.top_filter_phase = 0
        self.top_filter_index = 0

        self.is_framed = False

        self.clipping_type = 0
        self.clipping_map = None
        self.auto_extent_map = None
        self.auto_extent_margin = 0
        self.auto_extent_margin_units = 0
        self.auto_extent_layer = None
        self.clip_grid_and_graticules = False
        self.extent_type = 0

        self.default_time_interval = 0
        self.default_time_interval_units = 0
        self.default_time_window = None
        self.full_time_extent = None
        self.current_time_value = None
        self.time_reference = None
        self.current_time_extent = None
        self.display_time_format = ""
        self.display_each_timestamp = False
        self.display_speed = 10
        self.play_option = 0
        self.time_extent_option = 0
        self.time_definition_layer = None
        self.dynamic_time_refresh = False
        self.display_date_format = ""
        self.show_time = False
        self.has_live_data = False
        self.time_relation = 0
        self.show_time_on_display = False
        self.time_text_element = None

    def __repr__(self):
        if self.ref_id is not None:
            return "<Map: {} ({})>".format(self.name, self.ref_id)
        else:
            return "<Map: {}>".format(self.name)

    @staticmethod
    def compatible_versions():
        return [9, 19, 22, 29, 30, 31, 35, 37, 44, 45, 51, 52]

    def read(self, stream: Stream, version):
        self.name = stream.read_string("name")
        self.description = stream.read_string("description")
        self.crs = stream.read_object("crs")

        # layer count?
        layer_count = stream.read_int("root layer/group count")
        for i in range(layer_count):
            size = -1
            start = stream.tell()
            if version > 22:
                res = stream.read_ushort("unknown", expected=(1, 2, 3))
                if res in (2, 3):
                    # maybe not ushort??
                    size = stream.read_int("size") + 10
                    stream.read_int("unknown")
            elif version > 9:
                size = stream.read_int("size") + 8
                stream.read_int("unknown", expected=0)

            try:
                self.root_groups.append(
                    stream.read_object(
                        "root group {}".format(i + 1), expected_size=size
                    )
                )
            except CustomExtensionClsidException as e:
                self.root_groups.append(e.custom_object)
                stream.seek(start + size)

            if not stream.tolerant and size >= 0:
                assert stream.tell() == start + size, (stream.tell(), start + size)

        if version <= 22:
            stream.read_int("unknown", expected=0)

        stream.read_ushort("unknown flag", expected=65535)
        stream.read_ushort("unknown flag", expected=65535)

        self.graphics_layer = stream.read_object("graphics layer")
        if version > 19 and version <= 22:
            # possibly could be something in CompositeGraphicsLayer v <6
            stream.read_int("unknown", expected=0)
            stream.read_ushort("unknown", expected=0)

        count = stream.read_int("count")
        for i in range(count):
            self.elements.append(stream.read_object("element {}".format(i + 1)))

        # full extent
        self.full_extent_x_min = stream.read_double("full extent x min")
        self.full_extent_y_min = stream.read_double("full extent y min")
        self.full_extent_x_max = stream.read_double("full extent x max")
        self.full_extent_y_max = stream.read_double("full extent y max")

        self.map_units = stream.read_int("map units")
        self.distance_units = stream.read_int("distance units")

        self.area_of_interest = stream.read_object("area of interest")

        bookmark_count = stream.read_int("number of bookmarks")
        for i in range(bookmark_count):
            self.bookmarks.append(stream.read_object("bookmark {}".format(i + 1)))

        stream.read_ushort("unknown flag", expected=65535)

        self.verbose_events = stream.read_ushort("verbose events") != 0
        self.reference_scale = stream.read_double("reference scale")
        self.use_symbol_levels = stream.read_ushort("use symbol levels") != 0

        count = stream.read_int("standalone table count")
        for i in range(count):
            self.standalone_tables.append(
                stream.read_object("standalone table {}".format(i + 1))
            )

        self.illumination_properties = stream.read_object("illumination")

        self.conserve_memory = stream.read_ushort("conserve memory") != 0
        stream.read_ushort("unknown", expected=0)
        stream.read_int("output band size")
        self.delay_background_draw = stream.read_ushort("delay background draw") != 0
        self.expanded = stream.read_ushort("not expanded") == 0

        self.clipping_path = stream.read_object("clipping path")
        self.clipping_border = stream.read_object("clipping border")

        # this may be a count?
        stream.read_ushort("unknown", expected=(0, 1, 3))
        stream.read_object("unknown layer")
        stream.read_ushort("unknown", expected=0)
        stream.read_object("unknown extent")

        stream.read_ushort("unknown flag", expected=65535)
        stream.read_ushort("unknown flag", expected=65535)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)

        self.top_filter_phase = stream.read_int("top filter phase")
        self.top_filter_index = stream.read_int("top filter index")

        stream.read_ushort("unknown", expected=32)

        if version > 9:
            self.rotation = stream.read_double("rotation")

            count = stream.read_int("transformations count")
            for i in range(count):
                stream.read_int("index")  # , expected=i)
                self.transformations.append(stream.read_object("transform"))

            stream.read_double("last map scale??")
            stream.read_ushort("unknown", expected=(0, 1, 65535))

            self.background = stream.read_object("background")
            self.overposter_properties = stream.read_object(
                "basic overposter properties"
            )

        if version > 22:
            self.cache_build_when_map_extent_changes = (
                stream.read_ushort("build cache when map extent changes") != 0
            )
            self.cache_minimum_scale = stream.read_double(
                "minimum scale for auto cache"
            )
            self.case_use_minimum_scale = (
                stream.read_ushort("use minimum scale for auto cache") != 0
            )

            self.initial_view = stream.read_object("unknown envelope")
            stream.read_object("unknown envelope 2")
            stream.read_double("unknown scale")
            stream.read_object("unknown extent")
            stream.read_object("unknown extent 2")
            stream.read_double("unknown scale")

            stream.read_int("unknown width (px)")
            stream.read_int("unknown height (px)")

            stream.read_int("last map width (px)")
            stream.read_int("last map height (px)")

            stream.read_int("unknown width (px)")
            stream.read_int("unknown height (px)")
            stream.read_int("unknown width (px)")
            stream.read_int("unknown height (px)")

        if version > 29:
            stream.read_ushort("unknown", expected=(1, 2))
            count = stream.read_int("masked count")
            for i in range(count):
                masked_layer = stream.read_object(
                    "masked layer {}".format(i + 1), expect_existing=True
                )
                masking_count = stream.read_int("masked by count")
                masked = []
                for j in range(masking_count):
                    masked_by = stream.read_object(
                        "masked by layer {}".format(j + 1), expect_existing=True
                    )
                    if version > 30:
                        levels = stream.read_string("levels")
                    else:
                        levels = []
                    masked.append({"layer": masked_by, "levels": levels})
                self.masking[masked_layer] = masked

            self.draw_using_masking_options = (
                stream.read_ushort("draw using masking options") != 0
            )

        if version > 28:
            groups = []

            def count_groups(g):
                # likely subclasses of ICompositeLayer? (or ILayerMasking?)
                if isinstance(g, (GroupLayer,)):
                    groups.append(g)
                    if isinstance(g, GroupLayer):
                        for c in g.children:
                            count_groups(c)
                else:
                    return

            for g in self.root_groups:
                count_groups(g)

            if groups:
                for i in range(len(groups)):
                    stream.read_ushort(
                        "unknown masking related {}".format(i + 1), expected=(0, 1, 2)
                    )
                    masked_count = stream.read_int("number of masked layers in group")
                    for j in range(masked_count):
                        stream.read_object("layer BEING MASKED ref {}".format(j + 1))
                        masking_count = stream.read_int("number of masking layers")
                        for k in range(masking_count):
                            stream.read_object("LAYER MASKING ref {}".format(k + 1))
                            stream.read_string("symbol levels")

                    stream.read_ushort(
                        "unknown masking related flag {}".format(i + 1),
                        expected=(0, 65535),
                    )

            if version < 30:
                stream.read_int("unknown c", expected=(0, 1))
                stream.read_ushort("unknown d", expected=0)
                stream.read_ushort("unknown e", expected=(0, 1))

            self.is_framed = stream.read_ushort("is framed") != 0

        if version > 29:
            self.credits = stream.read_string("project credits")

        if version > 30:
            self.simulate_layer_transparency_in_legends = (
                stream.read_ushort("simulate layer transparency in legends") != 0
            )

        if version > 34:
            stream.read_uchar("unknown", expected=0)
            count = stream.read_int("count of clipping exempt layers")
            for i in range(count):
                self.clipping_exempt_layers.append(
                    stream.read_object("clipping exempt layer {}".format(i + 1))
                )

            self.clipping_type = stream.read_int("clipping type")
            self.clipping_map = stream.read_object("linked map")  # clipping map
            self.extent_type = stream.read_int("extent type")  # esriExtentTypeEnum
            self.fixed_scale = stream.read_double("fixed scale")
            self.fixed_extent = stream.read_object("fixed extent")
            self.auto_extent_map = stream.read_object("auto extent map")
            self.auto_extent_margin = stream.read_double("auto extent margin")
            self.auto_extent_margin_units = stream.read_int("auto extent margin units")
            self.auto_extent_layer = stream.read_object("auto extent layer")

            self.clip_grid_and_graticules = (
                stream.read_ushort("clip grid and graticules") != 0
            )

        if version > 35:
            scale_count = stream.read_int("scale count")
            for i in range(scale_count):
                self.scales.append(stream.read_double("scale {}".format(i + 1)))

            stream.read_int("unknown", expected=0)

        if version > 37:
            self.default_time_interval = stream.read_double("default time interval")
            self.default_time_interval_units = stream.read_int(
                "default time interval units"
            )
            self.default_time_window = stream.read_double("default time window")
            self.full_time_extent = stream.read_object("full time extent")
            self.current_time_value = stream.read_object(
                "current time value (instant or extent)"
            )
            self.time_reference = stream.read_object("time reference")
            self.current_time_extent = stream.read_object("current time extent")

            stream.read_ushort("unknown flag", expected=65535)
            stream.read_ushort("unknown flag", expected=65535)

            self.display_time_format = stream.read_string("display time format")
            self.display_each_timestamp = (
                stream.read_ushort("display each timestamp") != 0
            )
            self.display_speed = stream.read_int(
                "display speed", expected=(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
            )
            self.play_option = stream.read_int("play option (behavior after finishing)")

            if version == 44:
                stream.read_ushort("unknown")

            self.time_extent_option = stream.read_int("time extent option")
            self.time_definition_layer = stream.read_object(
                "time extent definition layer"
            )

            self.dynamic_time_refresh = stream.read_ushort("dynamic time refresh") != 0
            self.display_date_format = stream.read_string("display date format")

            stream.read_object("another time instance")

        if version > 44:
            self.show_time = stream.read_ushort("show time") != 0

        if version > 45:
            self.has_live_data = stream.read_ushort("has live data") != 0
            self.time_relation = stream.read_int("time relation")

            self.show_time_on_display = stream.read_ushort("show time on display") != 0
            self.time_text_element = stream.read_object("time text element")

        if version > 51:
            self.allow_assignment_of_unique_ids_for_publishing = (
                stream.read_ushort("allow assignment of unique ids for publishing") != 0
            )

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "name": self.name,
            "description": self.description,
            "credits": self.credits,
            "crs": self.crs.to_dict() if self.crs else None,
            "root_groups": [g.to_dict() for g in self.root_groups],
            "graphics_layer": self.graphics_layer.to_dict()
            if self.graphics_layer
            else None,
            "illumination_properties": self.illumination_properties.to_dict()
            if self.illumination_properties
            else None,
            "overposter_properties": self.overposter_properties.to_dict()
            if self.overposter_properties
            else None,
            "fixed_extent": self.fixed_extent.to_dict() if self.fixed_extent else None,
            "fixed_scale": self.fixed_scale,
            "rotation": self.rotation,
            "simulate_layer_transparency_in_legends": self.simulate_layer_transparency_in_legends,
            "map_units": Units.distance_unit_to_string(self.map_units),
            "distance_units": Units.distance_unit_to_string(self.distance_units),
            "allow_assignment_of_unique_ids_for_publishing": self.allow_assignment_of_unique_ids_for_publishing,
            "background": self.background.to_dict() if self.background else None,
            "bookmarks": [b.to_dict() for b in self.bookmarks],
            "standalone_tables": [t.to_dict() for t in self.standalone_tables],
            "transformations": [t.to_dict() for t in self.transformations],
            "cache_build_when_map_extent_changes": self.cache_build_when_map_extent_changes,
            "cache_minimum_scale": self.cache_minimum_scale,
            "case_use_minimum_scale": self.case_use_minimum_scale,
            "clipping_path": self.clipping_path.to_dict()
            if self.clipping_path
            else None,
            "clipping_border": self.clipping_border.to_dict()
            if self.clipping_border
            else None,
            "clipping_exempt_layers": self.clipping_exempt_layers,
            "scales": self.scales,
            "elements": [e.to_dict() for e in self.elements],
            "draw_using_masking_options": self.draw_using_masking_options,
            "masking": self.masking,
            "full_extent_x_min": self.full_extent_x_min,
            "full_extent_y_min": self.full_extent_y_min,
            "full_extent_x_max": self.full_extent_x_max,
            "full_extent_y_max": self.full_extent_y_max,
            "area_of_interest": self.area_of_interest.to_dict()
            if self.area_of_interest
            else None,
            "verbose_events": self.verbose_events,
            "reference_scale": self.reference_scale,
            "use_symbol_levels": self.use_symbol_levels,
            "conserve_memory": self.conserve_memory,
            "output_band_size": self.output_band_size,
            "delay_background_draw": self.delay_background_draw,
            "expanded": self.expanded,
            "top_filter_phase": self.top_filter_phase,
            "top_filter_index": self.top_filter_index,
            "is_framed": self.is_framed,
            "clipping_type": self.clipping_type,
            "clipping_map": self.clipping_map,
            "auto_extent_map": self.auto_extent_map,
            "auto_extent_margin": self.auto_extent_margin,
            "auto_extent_margin_units": self.auto_extent_margin_units,
            "auto_extent_layer": self.auto_extent_layer,
            "clip_grid_and_graticules": self.clip_grid_and_graticules,
            "extent_type": self.extent_type,
            "default_time_interval": self.default_time_interval,
            "default_time_interval_units": self.default_time_interval_units,
            "default_time_window": self.default_time_window,
            "full_time_extent": self.full_time_extent.to_dict()
            if self.full_time_extent
            else None,
            "current_time_value": self.current_time_value.to_dict()
            if self.current_time_value
            else None,
            "time_reference": self.time_reference.to_dict()
            if self.time_reference
            else None,
            "current_time_extent": self.current_time_extent.to_dict()
            if self.current_time_extent
            else None,
            "display_time_format": self.display_time_format,
            "display_each_timestamp": self.display_each_timestamp,
            "display_speed": self.display_speed,
            "play_option": self.play_option,
            "time_extent_option": self.time_extent_option,
            "time_definition_layer": self.time_definition_layer,
            "dynamic_time_refresh": self.dynamic_time_refresh,
            "display_date_format": self.display_date_format,
            "show_time": self.show_time,
            "has_live_data": self.has_live_data,
            "time_relation": self.time_relation,
            "show_time_on_display": self.show_time_on_display,
            "time_text_element": self.time_text_element.to_dict()
            if self.time_text_element
            else None,
        }
