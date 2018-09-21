from slyr.parser.object_registry import REGISTRY

from slyr.parser.objects.line_template import *
from slyr.parser.objects.colors import *
from slyr.parser.objects.decoration import *
from slyr.parser.objects.line_symbol_layer import *
from slyr.parser.objects.fill_symbol_layer import *
from slyr.parser.objects.marker_symbol_layer import *
from slyr.parser.objects.font import *
from slyr.parser.symbol_parser import *


def initialize_registry():
    REGISTRY.register(LineTemplate)
    REGISTRY.register(CMYKColor)
    REGISTRY.register(RgbColor)
    REGISTRY.register(HSVColor)
    REGISTRY.register(HSLColor)
    REGISTRY.register(GrayColor)
    REGISTRY.register(LineDecoration)
    REGISTRY.register(SimpleLineDecoration)
    REGISTRY.register(SimpleLineSymbolLayer)
    REGISTRY.register(CartographicLineSymbolLayer)
    REGISTRY.register(MarkerLineSymbolLayer)
    REGISTRY.register(SimpleFillSymbolLayer)
    REGISTRY.register(ArrowMarkerSymbolLayer)
    REGISTRY.register(CharacterMarkerSymbolLayer)
    REGISTRY.register(SimpleMarkerSymbolLayer)
    REGISTRY.register(Font)
    REGISTRY.register(FillSymbol)
    REGISTRY.register(LineSymbol)
    REGISTRY.register(MarkerSymbol)
