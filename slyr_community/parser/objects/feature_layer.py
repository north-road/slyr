#!/usr/bin/env python
"""
FeatureLayer

This is the big one. It contains all the useful properties regarding a layer.

PARTIAL INTERPRETATION:
- renderers are done
- some general layer properties are done
- field properties are done
- annotation/labeling has partial support
- many unimplemented objects follow labeling - some are general layer properties, others more specialised (like map tips)
"""

from ..object import Object
from ..stream import Stream
from .units import Units
from ..exceptions import (
    UnknownClsidException,
    NotImplementedException,
    CustomExtensionClsidException,
)
from .geometry import Geometry


class CustomRenderer(Object):
    """
    Represents a custom renderer which could not be parsed
    """

    def __init__(self, clsid):
        super().__init__()
        self.clsid = clsid

    def to_dict(self):  # pylint: disable=method-hidden
        return {"clsid": self.clsid}


class FeatureLayer(Object):
    """
    FeatureLayer
    """

    HYPERLINK_DOCUMENT = 0
    HYPERLINK_URL = 1
    HYPERLINK_MACRO = 2
    HYPERLINK_SCRIPT = 3

    JOIN_TYPE_LEFT_OUTER = 0
    JOIN_TYPE_LEFT_INNER = 1

    HTML_POPUP_TWO_COLUMN_TABLE = 0
    HTML_POPUP_REDIRECTED = 1
    HTML_POPUP_XSL = 2

    SEARCH_ORDER_SPATIAL_FIRST = 0
    SEARCH_ORDER_ATTRIBUTE_FIRST = 1

    @staticmethod
    def cls_id():
        return "e663a651-8aad-11d0-bec7-00805f7c4268"

    def __init__(self):  # pylint: disable=too-many-statements
        super().__init__()
        self.name = ""
        self.description = ""
        self.datasource_type = ""
        self.dataset_name = None
        self.renderer = None
        self.field_info = {}
        self.legend_group = None
        self.definition_query = None
        self.definition_search_order = FeatureLayer.SEARCH_ORDER_SPATIAL_FIRST
        self.cached = False

        self.display_field = ""

        self.zoom_max = 0
        self.zoom_min = 0

        # used when a zoom range has been set previously, but is currently disabled
        self.stored_zoom_max = 0
        self.stored_zoom_min = 0

        self.visible = True
        self.labels_enabled = False
        self.annotation_collection = None
        self.display_filter = None
        self.hyperlink_type = FeatureLayer.HYPERLINK_DOCUMENT
        self.hyperlink_field = None
        self.hyperlink_macro_name = ""
        self.scale_symbols = True

        self.selection_color = None
        self.selected_feature_symbol = None
        self.show_selection_using_symbol = False

        self.show_map_tips = False
        self.layer_extent = None
        self.features_excluded_from_rendering = None
        self.uid = None
        self.transparency = 0
        self.brightness = 0
        self.map_tip_hide_field_name = False
        self.map_tip_show_coded = False
        self.map_tip_field_name = ""
        self.map_tip_url_prefix = ""
        self.map_tip_url_suffix = ""
        self.map_tip_xsl = ""
        self.html_popup_enabled = False
        self.html_popup_style = FeatureLayer.HTML_POPUP_TWO_COLUMN_TABLE
        self.html_popup_download_attachment = False
        self.use_advanced_symbol_levels = False

        self.time_enabled = False
        self.time_zone = None
        self.time_step = 0
        self.time_step_units = Units.TIME_UNITS_UNKNOWN
        self.time_offset = 0
        self.time_offset_units = Units.TIME_UNITS_UNKNOWN
        self.time_data_changes_regularly = False
        self.time_format = ""
        self.time_display_cumulative = False
        self.time_field = ""
        self.end_time_field = ""
        self.time_extent = None
        self.time_dimension_name = ""
        self.time_dimension_format = ""
        self.track_id_field_name = ""

        self.display_expression_properties = None

        self.extensions = []

        self.join_type = FeatureLayer.JOIN_TYPE_LEFT_INNER
        self.join = None
        self.relations = []
        self.hyperlinks = []
        self.hyperlink_expression_properties = None

        self.selection_set = []
        self.selectable = True

        self.weight = 0

        self.shape_type = Geometry.GEOMETRY_ANY

        self.use_page_definition_query = False
        self.page_name_field = ""
        self.page_name_match_operator = ""

        self.area_of_interest = None

    def __repr__(self):
        if self.ref_id is not None:
            return "<FeatureLayer: {} ({})>".format(self.name, self.ref_id)
        else:
            return "<FeatureLayer: {}>".format(self.name)

    @staticmethod
    def compatible_versions():
        return [6, 15, 16, 17, 18, 21, 22, 23, 24, 25, 33, 34]

    @staticmethod
    def hyperlink_type_to_string(hyperlink):
        """
        Converts a hyperlink type to a string
        """
        if hyperlink == FeatureLayer.HYPERLINK_DOCUMENT:
            return "document"
        elif hyperlink == FeatureLayer.HYPERLINK_URL:
            return "url"
        elif hyperlink == FeatureLayer.HYPERLINK_MACRO:
            return "macro"
        elif hyperlink == FeatureLayer.HYPERLINK_SCRIPT:
            return "script"
        return None

    @staticmethod
    def join_type_to_string(join):
        """
        Converts a join type to string
        """
        if join == FeatureLayer.JOIN_TYPE_LEFT_OUTER:
            return "left_outer"
        elif join == FeatureLayer.JOIN_TYPE_LEFT_INNER:
            return "left_inner"
        return None

    @staticmethod
    def html_popup_style_to_string(style):
        """
        Converts a HTML popup style to string
        """
        if style == FeatureLayer.HTML_POPUP_TWO_COLUMN_TABLE:
            return "two_column_table"
        elif style == FeatureLayer.HTML_POPUP_REDIRECTED:
            return "redirected"
        elif style == FeatureLayer.HTML_POPUP_XSL:
            return "xsl"
        return None

    @staticmethod
    def search_order_to_string(order):
        """
        Converts a search order to string
        """
        if order == FeatureLayer.SEARCH_ORDER_SPATIAL_FIRST:
            return "spatial_first"
        elif order == FeatureLayer.SEARCH_ORDER_ATTRIBUTE_FIRST:
            return "attribute_first"
        assert False

    def read(self, stream: Stream, version):  # pylint: disable=too-many-locals,too-many-return-statements,too-many-branches,too-many-statements
        self.name = stream.read_string("name")
        self.datasource_type = stream.read_string("datasource_type")
        self.visible = stream.read_ushort("visible") != 0
        self.show_map_tips = stream.read_ushort("show map tips") != 0

        self.cached = stream.read_ushort("cached") != 0

        self.dataset_name = stream.read_object("dataset name")
        try:
            self.renderer = stream.read_object("renderer")
        except CustomExtensionClsidException as e:
            self.renderer = CustomRenderer(e.clsid)
            raise e

        stream.read_raw_clsid(
            "renderer properties page",
            expected=(
                "4eab5691-8f9c-11d2-ab21-00c04fa334b3",
                "683c994e-a17b-11d1-8816-080009ec732a",  # UniqueValuePropertyPage
                "00000000-0000-0000-0000-000000000000",
                "683c994f-a17b-11d1-8816-080009ec732a",  # GraduatedColorPropertyPage
                "683c994e-a17b-11d1-8816-080009ec732a",
                "68e95091-e60d-11d2-9f31-00c04f6bc709",
                "90c47e6f-a102-11d2-ab24-00c04fa334b3",
                "4eab5691-8f9c-11d2-ab21-00c04fa334b3",
                "ae1248b6-cd1e-11d2-9f25-00c04f6bc709",  # BiUniqueValuePropertyPage
                "d2025f16-0502-11d4-9f7c-00c04f6bc709",  # MultiDotDensityPropertyPage
                "f891fe58-e796-11d2-9f31-00c04f6bc709",  # ProportionalSymbolPropertyPage
                "f891fe57-e796-11d2-9f31-00c04f6bc709",  # GraduatedSymbolPropertyPage
                "98dd703f-feb4-11d3-9f7c-00c04f6bc709",  # BarChartPropertyPage
                "98dd7040-feb4-11d3-9f7c-00c04f6bc709",  # PieChartPropertyPage
                "6cacdfe6-aed2-49b0-812e-085169dd4917",  # CadUniqueValuePropertyPage
                "7cd6ef8c-7c5f-4051-920b-3b0baacbe5ca",  # RepresentationRulesPropertyPage
                "98dd7041-feb4-11d3-9f7c-00c04f6bc709",
            ),
        )  # StackedChartPropertyPage

        self.display_field = stream.read_string("display field")

        self.zoom_max = stream.read_double("zoom max")
        self.zoom_min = stream.read_double("zoom min")

        self.labels_enabled = stream.read_ushort("labels enabled") != 0

        count = stream.read_int("link count")
        for i in range(count):
            self.hyperlinks.append(stream.read_object("hyperlink {}".format(i + 1)))

        self.selection_color = stream.read_object("selection color")

        self.definition_query = stream.read_string("query")

        self.hyperlink_field = stream.read_string("hyperlink field")
        self.hyperlink_type = stream.read_int("hyperlink type")

        classes = stream.read_uint("field info count")
        for i in range(classes):
            key = stream.read_string("key")
            self.field_info[key] = stream.read_object("field {}".format(i + 1))

        self.annotation_collection = stream.read_object("annotation collection")

        self.show_selection_using_symbol = (
            stream.read_ushort("show_selection_using_symbol") != 0
        )

        self.features_excluded_from_rendering = stream.read_object("excluded features")
        count = stream.read_int("selection set")
        for i in range(count):
            self.selection_set.append(stream.read_int("selection {}".format(i + 1)))

        self.scale_symbols = stream.read_ushort("scale symbols") != 0

        self.display_filter = stream.read_object("display filter")
        self.transparency = stream.read_ushort("transparency")
        self.brightness = stream.read_ushort("brightness")

        stream.read_ushort("unknown", expected=0)
        if version >= 15:
            self.join_type = stream.read_int("join type")
        self.join = stream.read_object("join")

        if version < 16:
            stream.read_string("unknown folder path", expected="")

        if version < 15:
            return

        rel_count = stream.read_int("number of relationships")
        for i in range(rel_count):
            self.relations.append(stream.read_object("relation {}".format(i + 1)))

        self.hyperlink_macro_name = stream.read_string("hyperlink macro name")
        self.area_of_interest = stream.read_object("area of interest")

        stream.read_index_array("unknown index array")

        if version >= 15:
            remote_count = stream.read_int("remote object count")
            for i in range(remote_count):
                size = (
                    stream.read_int("size {}".format(i)) + 20
                )  # 20 = object header size
                pos = stream.tell()
                stream.read_int("unknown", expected=0)

                if size == 20:
                    stream.read_raw_clsid("Empty object ref")
                    continue

                try:
                    obj = stream.read_object(
                        "remote object", allow_reference=False, expected_size=size
                    )
                    self.extensions.append(obj)
                    assert stream.tell() == pos + size, (
                        "Expected length {} got length {}".format(
                            size, stream.tell() - pos
                        )
                    )
                except UnknownClsidException:
                    # don't know this object
                    stream.read(size - 20)
                except NotImplementedException:
                    # don't know this object
                    stream.read(size - 20)

                # NOTE - ServerLayerExtension includes layer copyright text

        self.weight = stream.read_double(
            "weight", expected=(-1.0, 50.0, 97.0, 98.0, 99.0, 100.0)
        )
        self.selected_feature_symbol = stream.read_object("selected feature symbol")
        self.selectable = stream.read_ushort("selectable") != 0
        self.shape_type = stream.read_int("shape type")
        self.layer_extent = stream.read_object("layer extent")

        if version <= 16:
            return

        self.uid = stream.read_object("uid")

        if version <= 17:
            return

        self.description = stream.read_string("layer description")

        stream.read_ushort("unknown flag", expected=(0, 65535))

        self.stored_zoom_max = stream.read_double("stored zoom max")
        self.stored_zoom_min = stream.read_double("stored zoom min")

        self.use_advanced_symbol_levels = (
            stream.read_ushort("use advanced symbol levels") == 0
        )

        if version <= 21:
            return

        self.definition_search_order = stream.read_int("definition query search order")

        if version <= 22:
            return

        stream.read_ushort("unknown flag", expected=(0, 65535))

        if version <= 23:
            return

        count = stream.read_int("unknown count")
        for i in range(count):
            stream.read_string("unknown filter?", expected="")
            stream.read_string("unknown?", expected="")

        if version <= 24:
            return

        self.html_popup_style = stream.read_int("html popup style")
        self.html_popup_enabled = stream.read_ushort("html popups enabled") != 0

        # map tips
        self.map_tip_hide_field_name = (
            stream.read_ushort("map tip hide field name") != 0
        )
        self.map_tip_show_coded = stream.read_ushort("map tip show coded") != 0
        self.map_tip_field_name = stream.read_string("map tip field name")
        self.map_tip_url_prefix = stream.read_string("url prefix")
        self.map_tip_url_suffix = stream.read_string("url suffix")
        self.map_tip_xsl = stream.read_string("xsl")

        if version > 25:
            self.display_expression_properties = stream.read_object(
                "display expression properties"
            )

            self.use_page_definition_query = (
                stream.read_ushort("use page definition query") != 0
            )
            self.page_name_field = stream.read_string("page name field")
            self.page_name_match_operator = stream.read_string(
                "page name match operator"
            )
            stream.read_string("current page name value")

            # time stuff
            time_something = stream.read_ushort(
                "unknown time related?"
            )  # time dimensions??
            self.time_enabled = stream.read_ushort("time enabled") != 0
            self.time_zone = stream.read_object("time zone")
            self.time_data_changes_regularly = (
                stream.read_ushort("data changes regularly recalculate") != 0
            )
            if time_something > 1:  # maybe a count??
                stream.read_ushort("unknown", expected=1)
            self.time_field = stream.read_string("time field")
            self.end_time_field = stream.read_string("end time field")
            self.time_format = stream.read_string("time format")
            self.track_id_field_name = stream.read_string("track id field name")
            self.time_extent = stream.read_object("time extent")

            stream.read_ushort("unknown", expected=1)
            self.time_dimension_name = stream.read_string("time dimension name")
            self.time_dimension_format = stream.read_string("time dimension format")
            stream.read_ushort("unknown", expected=1)

            self.time_display_cumulative = (
                stream.read_ushort("time display cumulative") != 0
            )

            # time step and units
            self.time_step = stream.read_double("time step")
            self.time_step_units = stream.read_int("time step units")

            # time offset and units
            self.time_offset = stream.read_double("time offset")
            self.time_offset_units = stream.read_int("time offset units")

            self.hyperlink_expression_properties = stream.read_object(
                "hyperlink expression properties"
            )

            if version > 33:
                self.html_popup_download_attachment = (
                    stream.read_ushort("HTML popup download attachments") != 0
                )

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "name": self.name,
            "description": self.description,
            "datasource_type": self.datasource_type,
            "dataset_name": self.dataset_name.to_dict() if self.dataset_name else None,
            "renderer": self.renderer.to_dict() if self.renderer else None,
            "field_format": {k: v.to_dict() for k, v in self.field_info.items()},
            "visible": self.visible,
            "zoom_min": self.zoom_min,
            "zoom_max": self.zoom_max,
            "stored_zoom_min": self.stored_zoom_min,
            "stored_zoom_max": self.stored_zoom_max,
            "definition_query": self.definition_query,
            "definition_query_search_order": FeatureLayer.search_order_to_string(
                self.definition_search_order
            ),
            "labels_enabled": self.labels_enabled,
            "annotation_collection": self.annotation_collection.to_dict()
            if self.annotation_collection
            else None,
            "display_filter": self.display_filter.to_dict()
            if self.display_filter
            else None,
            "transparency": self.transparency,
            "brightness": self.brightness,
            "hyperlink_type": FeatureLayer.hyperlink_type_to_string(
                self.hyperlink_type
            ),
            "hyperlink_field": self.hyperlink_field,
            "hyperlink_macro_name": self.hyperlink_macro_name,
            "scale_symbols": self.scale_symbols,
            "selection_color": self.selection_color.to_dict()
            if self.selection_color
            else None,
            "show_selection_using_symbol": self.show_selection_using_symbol,
            "cached": self.cached,
            "show_map_tips": self.show_map_tips,
            "selected_feature_symbol": self.selected_feature_symbol.to_dict()
            if self.selected_feature_symbol
            else None,
            "layer_extent": self.layer_extent.to_dict() if self.layer_extent else None,
            "features_excluded_from_rendering": self.features_excluded_from_rendering.to_dict()
            if self.features_excluded_from_rendering
            else None,
            "uid": self.uid.to_dict() if self.uid else None,
            "display_expression_properties": self.display_expression_properties.to_dict()
            if self.display_expression_properties
            else None,
            "map_tip_hide_field_name": self.map_tip_hide_field_name,
            "map_tip_show_coded": self.map_tip_show_coded,
            "map_tip_field_name": self.map_tip_field_name,
            "map_tip_url_prefix": self.map_tip_url_prefix,
            "map_tip_url_suffix": self.map_tip_url_suffix,
            "map_tip_xsl": self.map_tip_xsl,
            "html_popup_enabled": self.html_popup_enabled,
            "html_popup_style": FeatureLayer.html_popup_style_to_string(
                self.html_popup_style
            ),
            "html_popup_download_attachment": self.html_popup_download_attachment,
            "use_advanced_symbol_levels": self.use_advanced_symbol_levels,
            "time_enabled": self.time_enabled,
            "time_zone": self.time_zone.to_dict() if self.time_zone else None,
            "time_step": self.time_step,
            "time_step_units": Units.time_unit_to_string(self.time_step_units),
            "time_offset": self.time_offset,
            "time_offset_units": Units.time_unit_to_string(self.time_offset_units),
            "time_data_changes_regularly": self.time_data_changes_regularly,
            "time_format": self.time_format,
            "time_display_cumulative": self.time_display_cumulative,
            "time_field": self.time_field,
            "time_end_field": self.end_time_field,
            "time_extent": self.time_extent.to_dict() if self.time_extent else None,
            "time_dimension_name": self.time_dimension_name,
            "time_dimension_format": self.time_dimension_format,
            "track_id_field_name": self.track_id_field_name,
            "extensions": [e.to_dict() for e in self.extensions],
            "join_type": FeatureLayer.join_type_to_string(self.join_type),
            "join": self.join.to_dict() if self.join else None,
            "relations": [r.to_dict() for r in self.relations],
            "hyperlinks": [h.to_dict() for h in self.hyperlinks],
            "selection_set": self.selection_set,
            "hyperlink_expression_properties": self.hyperlink_expression_properties.to_dict()
            if self.hyperlink_expression_properties
            else None,
            "selectable": self.selectable,
            "weight": self.weight,
            "shape_type": Geometry.geometry_type_to_string(self.shape_type),
            "use_page_definition_query": self.use_page_definition_query,
            "page_name_field": self.page_name_field,
            "page_name_match_operator": self.page_name_match_operator,
            "display_field": self.display_field,
            "area_of_interest": self.area_of_interest.to_dict()
            if self.area_of_interest
            else None,
        }
