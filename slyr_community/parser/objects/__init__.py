"""
Serializable objects
"""

# don't get fancy... too many issues with plugin reloads after updates when trying to do this dynamically


from slyr_community.parser.objects.texture_line_symbol import TextureLineSymbol
from slyr_community.parser.objects.picture import Picture, StdPicture, BmpPicture, EmfPicture
from slyr_community.parser.objects.simple_line3d_symbol import SimpleLine3DSymbol
from slyr_community.parser.objects.marker_symbol_layer import MarkerSymbolLayer, SimpleMarkerSymbol, \
    CharacterMarkerSymbol, \
    ArrowMarkerSymbol, PictureMarkerSymbol
from slyr_community.parser.objects.line_symbol_layer import LineSymbolLayer, SimpleLineSymbol, CartographicLineSymbol, \
    MarkerLineSymbol, HashLineSymbol, PictureLineSymbol
from slyr_community.parser.objects.line_template import LineTemplate
from slyr_community.parser.objects.decoration import LineDecoration, SimpleLineDecorationElement
from slyr_community.parser.objects.simple_marker3d_symbol import SimpleMarker3DSymbol
from slyr_community.parser.objects.font import Font
from slyr_community.parser.objects.ramps import ColorRamp, RandomColorRamp, PresetColorRamp, MultiPartColorRamp, \
    AlgorithmicColorRamp
from slyr_community.parser.objects.fill_symbol_layer import FillSymbolLayer, SimpleFillSymbol, ColorSymbol, \
    GradientFillSymbol, \
    LineFillSymbol, MarkerFillSymbol, PictureFillSymbol
from slyr_community.parser.objects.texture_fill_symbol import TextureFillSymbol
from slyr_community.parser.objects.marker3d_symbol import Marker3DSymbol
from slyr_community.parser.objects.symbol_layer import SymbolLayer
from slyr_community.parser.objects.color_ramp_symbol import ColorRampSymbol
from slyr_community.parser.objects.colors import Color, RgbColor, CmykColor, HsvColor, HlsColor, GrayColor
from slyr_community.parser.objects.character_marker3d_symbol import CharacterMarker3DSymbol
from slyr_community.parser.objects.multi_layer_symbols import MultiLayerSymbol, MultiLayerLineSymbol, \
    MultiLayerFillSymbol, \
    MultiLayerMarkerSymbol
from slyr_community.parser.objects.geometry_material import GeometryMaterial
from slyr_community.parser.objects.multi_patch import MultiPatch
from slyr_community.parser.objects.dot_density_fill_symbol import DotDensityFillSymbol
