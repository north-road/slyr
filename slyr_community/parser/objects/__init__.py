"""
Serializable objects
"""

# don't get fancy... too many issues with plugin reloads after updates when trying to do this dynamically


from .texture_line_symbol import TextureLineSymbol
from .picture import Picture, StdPicture, BmpPicture, EmfPicture
from .simple_line3d_symbol import SimpleLine3DSymbol
from .marker_symbol_layer import MarkerSymbolLayer, SimpleMarkerSymbol, \
    CharacterMarkerSymbol, \
    ArrowMarkerSymbol, PictureMarkerSymbol
from .line_symbol_layer import LineSymbolLayer, SimpleLineSymbol, CartographicLineSymbol, \
    MarkerLineSymbol, HashLineSymbol, PictureLineSymbol
from .line_template import LineTemplate
from .decoration import LineDecoration, SimpleLineDecorationElement
from .simple_marker3d_symbol import SimpleMarker3DSymbol
from .font import Font
from .ramps import ColorRamp, RandomColorRamp, PresetColorRamp, MultiPartColorRamp, \
    AlgorithmicColorRamp
from .fill_symbol_layer import FillSymbolLayer, SimpleFillSymbol, ColorSymbol, \
    GradientFillSymbol, \
    LineFillSymbol, MarkerFillSymbol, PictureFillSymbol
from .texture_fill_symbol import TextureFillSymbol
from .marker3d_symbol import Marker3DSymbol
from .symbol_layer import SymbolLayer
from .color_ramp_symbol import ColorRampSymbol
from .colors import Color, RgbColor, CmykColor, HsvColor, HlsColor, GrayColor
from .character_marker3d_symbol import CharacterMarker3DSymbol
from .multi_layer_symbols import MultiLayerSymbol, MultiLayerLineSymbol, \
    MultiLayerFillSymbol, \
    MultiLayerMarkerSymbol
from .geometry_material import GeometryMaterial
from .multi_patch import MultiPatch
from .dot_density_fill_symbol import DotDensityFillSymbol
from .geometry import Geometry
from .feature_layer import FeatureLayer
from .vector_renderer import VectorRendererBase
from .unique_value_renderer import UniqueValueRenderer
from .class_breaks_renderer import ClassBreaksRenderer
from .proportional_symbol_renderer import ProportionalSymbolRenderer
from .chart_renderer import ChartRenderer
from .s52_renderer import S52Renderer
from .simple_renderer import SimpleRenderer
from .annotate_layer_properties_collection import AnnotateLayerPropertiesCollection
from .annotate_map_properties import AnnotateMapProperties
from .annotation_expression_parser import DisplayExpressionProperties
from .annotation_jscript_engine import AnnotationJScriptEngine
from .annotation_python_engine import AnnotationPythonEngine
from .annotation_vbscript_engine import AnnotationVBScriptEngine
from .array_of_filter_def import ArrayOfFilterDef
from .balloon_callout import BalloonCallout
from .bar_chart_symbol import BarChartSymbol
from .basic_overposter import BasicOverposter
from .basic_overposter_layer_properties import BasicOverposterLayerProperties
from .basic_overposter_properties import BasicOverposterProperties
from .bi_unique_value_renderer import BiUniqueValueRenderer
from .cad_annotation_layer import CadAnnotationLayer
from .cad_drawing_name import CadDrawingName
from .cad_drawing_object import CadDrawingObject
from .cad_feature_layer import CadFeatureLayer
from .cad_layer import CadLayer
from .coded_value_domain import CodedValueDomain
from .coverage_annotation_layer import CoverageAnnotationLayer
from .db_table_name import DBTableName
from .dimension_layer import DimensionLayer
from .dimension_shape import DimensionShape
from .dimension_style import DimensionStyle
from .dimension_styles import DimensionStyles
from .dot_density_renderer import DotDensityRenderer
from .edit_template import EditTemplate
from .edit_template_manager import EditTemplateManager
from .envelope import Envelope
from .feature_class_name import FeatureClassName, FgdbFeatureClassName, GpkgFeatureClassName, \
    GpkgFeatureClassQuery, TopologyName, CoverageFeatureClassName, CoverageName, WmsConnectionName, \
    RepresentationClassName
from .feature_dataset_name import FeatureDatasetName
from .feature_id_set import FeatureIDSet
from .fid_set import FidSet
from .field import Field
from .field_info import FieldInfo
from .fields import Fields
from .geographic_coordinate_system import GeographicCoordinateSystem
from .geometry_bag import GeometryBag
from .geometry_def import GeometryDef
from .group_layer import GroupLayer
from .hotlink_expression_properties import HotLinkExpressionProperties
from .hotlink_python_engine import HotlinkPythonEngine
from .hotlink_vbscript_engine import HotlinkVbscriptEngine
from .hyperlink import Hyperlink
from .index import Index
from .indexes import Indexes
from .label_engine_layer_properties import LabelEngineLayerProperties
from .label_style import LabelStyle
from .legend_class import LegendClass
from .legend_class_format import LegendClassFormat
from .legend_group import LegendGroup
from .legend_groups import LegendGroups
from .line_callout import LineCallout
from .line_label_placement_priorities import LineLabelPlacementPriorities
from .line_label_position import LineLabelPosition
from .long_array import LongArray
from .maplex_label_engine_layer_properties import MaplexLabelEngineLayerProperties
from .maplex_label_stacking_properties import MaplexLabelStackingProperties
from .maplex_label_style import MaplexLabelStyle
from .maplex_offset_along_line_properties import MaplexOffsetAlongLineProperties
from .maplex_overposter_layer_properties import MaplexOverposterLayerProperties
from .maplex_rotation_properties import MaplexRotationProperties
from .maplex_unknown import MaplexDictionaries, MaplexDictionary, MaplexDictionaryEntry, \
    MaplexOverposterProperties, MaplexPlacedLabel, MaplexKeyNumberGroups, MaplexKeyNumberGroup, MaplexAnnotateFeature, \
    MaplexAnnotateMap, MaplexOverposter
from .marker_text_background import MarkerTextBackground
from .memory_relationship_class_name import MemoryRelationshipClassName
from .multipoint import Multipoint
from .names import Names
from .network_dataset_name import NetworkDatasetName
from .network_layer import NetworkLayer
from .numeric_format import NumericFormat, FractionFormat, DirectionFormat, AngleFormat, PercentageFormat, CustomNumberFormat, \
    CurrencyFormat, LatLonFormat, RateFormat, ScientificFormat
from .pie_chart_symbol import PieChartSymbol
from .place import Place
from .point import Point
from .point_placement_priorities import PointPlacementPriorities
from .polygon import Polygon
from .polyline import Polyline
from .projected_coordinate_system import ProjectedCoordinateSystem
from .property_set import PropertySet
from .query_filter import QueryFilter
from .range_domain import RangeDomain
from .rel_query_table_name import RelQueryTableName
from .rendering_rule import RenderingRule
from .representation_renderer import RepresentationRenderer
from .representation_rule import RepresentationRule
from .route_anomaly_properties import RouteAnomalyProperties
from .route_event_source_name import RouteEventSourceName
from .route_identify_properties import RouteIdentifyProperties
from .route_layer_extension import RouteLayerExtension
from .route_measure_line_properties import RouteMeasureLineProperties
from .route_measure_locator_name import RouteMeasureLocatorName
from .route_measure_point_properties import RouteMeasurePointProperties
from .scale_dependent_renderer import ScaleDependentRenderer
from .server_layer_extension import ServerLayerExtension
from .simple_line_callout import SimpleLineCallout
from .simple_network_renderer import SimpleNetworkRenderer
from .spatial_filter import SpatialFilter
from .stacked_chart_symbol import StackedChartSymbol
from .standalone_table import StandaloneTable
from .str_array import StrArray
from .table_fields import TableFields
from .table_name import TableName, FgdbTableName
from .text_symbol import TextSymbol
from .time import Time
from .time_extent import TimeExtent
from .time_instant import TimeInstant
from .time_reference import TimeReference
from .time_zone import TimeZone
from .topology_layer import TopologyLayer
from .transparency_display_filter import TransparencyDisplayFilter
from .uid import UID
from .unknown_coordinate_system import UnknownCoordinateSystem
from .workspace_factory import (
    WorkspaceFactory,
    SdeWorkspaceFactory,
    AccessWorkspaceFactory,
    ArcInfoWorkspaceFactory,
    CadWorkspaceFactory,
    IMSWorkspaceFactory,
    OLEDBWorkspaceFactory,
    PCCoverageWorkspaceFactory,
    RasterWorkspaceFactory,
    ShapefileWorkspaceFactory,
    FileGDBWorkspaceFactory,
    TextFileWorkspaceFactory,
    TinWorkspaceFactory,
    VpfWorkspaceFactory,
    FeatureServiceWorkspaceFactory,
    SdcWorkspaceFactory,
    ExcelOrMdbWorkspaceFactory,
    GpkgWorkspaceFactory,
    FMEWorkspaceFactory,
    StreetMapWorkspaceFactory,
    LasDatasetWorkspaceFactory,
    NetCDFWorkspaceFactory,
    ToolboxWorkspaceFactory,
    S57WorkspaceFactory
)
from .workspace_name import WorkspaceName
from .xy_event2_fields_properties import XYEvent2FieldsProperties
from .xy_event_source_name import XYEventSourceName
from .raster_layer import RasterLayer
from .wmts_layer import WmtsLayer
from .wms_layer import WmsMapLayer, WmsGroupLayer, WmsLayer
from .tin_layer import TinLayer
from .raster_basemap_layer import RasterBasemapLayer
from .map_server_rest_layer import MapServerRESTLayer, MapServerRESTSubLayer
from .image_server_layer import ImageServerLayer, UnknownImageServerExtension1, \
    UnknownImageServerExtension2
from .internet_tiled_layer import InternetTiledLayer, MSVirtualEarthLayerProvider, TileCacheInfo, \
    OpenStreetMapProvider
from .las_dataset_layer import LasDatasetLayer
from .map_server_layer import MapServerLayer, MapServerSubLayer, MapServerBasicSublayer
from .base_map_layer import BaseMapLayer
from .raster_stretch_color_ramp_renderer import RasterStretchColorRampRenderer, \
    RedrawLegendClass
from .raster_dataset_name import RasterDatasetName2, RasterDatasetName, FgdbRasterDatasetName, \
    SdeRasterDatasetName, AccessRasterDatasetName
from .raster_rgb_renderer import RasterRGBRenderer, RasterRgbRendererColorComponents, \
    RasterRgbPanSharpeningProperties
from .stats_histogram import StatsHistogram
from .composite_xform import CompositeXForm
from .identify_xform import IdentityXForm
from .coordinate_xform import CoordinateXForm
from .raster_color_map_renderer import RasterColorMapRenderer
from .raster_unique_value_renderer import RasterUniqueValueRenderer
from .unique_values import UniqueValues
from .raster_band_name import RasterBandName
from .raster_discrete_color_renderer import RasterDiscreteColorRenderer
from .raster_classify_color_ramp_renderer import RasterClassifyColorRampRenderer
from .array_of_ishader import ArrayOfIShader
from .raster_band_collection_name import RasterBandCollectionName
from .raster_catalog_layer import RasterCatalogLayer
from .raster_catalog_name import RasterCatalogName
from .raster_def import RasterDef
from .raster_shader import RasterShader
from .raster_storage_def import RasterStorageDef
from .simple_raster_renderer import SimpleRasterRenderer
