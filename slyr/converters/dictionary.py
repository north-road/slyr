#!/usr/bin/env python

"""
Converts parsed symbol properties to a Python dictionary
"""

from typing import Union
from slyr.converters.converter import (
    Converter,
    NotImplementedException
)
from slyr.parser.symbol_parser import (
    FillSymbolLayer,
    Symbol,
    FillSymbol,
    LineSymbol,
    MarkerSymbol,
    MarkerSymbolLayer,
    LineTemplate
)
from slyr.parser.objects.symbol_layer import SymbolLayer
from slyr.parser.objects.line_symbol_layer import (
    LineSymbolLayer,
    SimpleLineSymbolLayer,
    CartographicLineSymbolLayer,
    MarkerLineSymbolLayer
)
from slyr.parser.objects.fill_symbol_layer import SimpleFillSymbolLayer
from slyr.parser.objects.marker_symbol_layer import (
    SimpleMarkerSymbolLayer,
    CharacterMarkerSymbolLayer,
    ArrowMarkerSymbolLayer,
)
from slyr.parser.objects.decoration import (
    LineDecoration,
    SimpleLineDecoration
)


class DictionaryConverter(Converter):
    """
    Converts symbols to a Python dictionary
    """

    def __init__(self):
        self.out = {}

    def convert_symbol(self, symbol: Symbol):
        self.out = {}
        super().convert_symbol(symbol)
        return self.out

    def convert_fill_symbol(self, symbol: Union[SymbolLayer, FillSymbol]):
        self.out = {
            'type': 'FillSymbol',
            'levels': []
        }
        if issubclass(symbol.__class__, SymbolLayer):
            self.out['levels'].append(self.convert_symbol_layer(symbol))
        else:
            for l in symbol.levels:
                self.out['levels'].append(self.convert_symbol_layer(l))

    def convert_line_symbol(self, symbol: Union[SymbolLayer, LineSymbol]):
        self.out = {
            'type': 'LineSymbol',
            'levels': []
        }
        if issubclass(symbol.__class__, SymbolLayer):
            self.out['levels'].append(self.convert_symbol_layer(symbol))
        else:
            for l in symbol.levels:
                self.out['levels'].append(self.convert_symbol_layer(l))

    def convert_marker_symbol(self, symbol: Union[SymbolLayer, MarkerSymbol]):
        self.out = {
            'type': 'MarkerSymbol',
            'levels': [],
            'halo': symbol.halo,
            'halo_size': symbol.halo_size,
            'halo_symbol_type': type(symbol.halo_symbol).__name__
        }

        if isinstance(symbol.halo_symbol, FillSymbol):
            halo_converter = DictionaryConverter()
            self.out['halo_symbol'] = halo_converter.convert_symbol(symbol.halo_symbol)

        if issubclass(symbol.__class__, SymbolLayer):
            self.out['levels'].append(self.convert_symbol_layer(symbol))
        else:
            for l in symbol.levels:
                self.out['levels'].append(self.convert_symbol_layer(l))

    def convert_symbol_layer(self, layer: SymbolLayer) -> dict:
        """
        Converts a SymbolLayer
        """
        if issubclass(layer.__class__, FillSymbolLayer):
            out = self.convert_fill_symbol_layer(layer)
        elif issubclass(layer.__class__, LineSymbolLayer):
            out = DictionaryConverter.convert_line_symbol_layer(layer)
        elif issubclass(layer.__class__, MarkerSymbolLayer):
            out = DictionaryConverter.convert_marker_symbol_layer(layer)
        else:
            raise NotImplementedException('{} not implemented yet'.format(layer.__class__))
        out['type'] = type(layer).__name__
        out['enabled'] = layer.enabled
        out['locked'] = layer.locked
        return out

    def convert_fill_symbol_layer(self, layer: FillSymbolLayer) -> dict:
        """
        Converts a FillSymbolLayer
        """
        if isinstance(layer, SimpleFillSymbolLayer):
            return self.convert_simple_fill_symbol_layer(layer)
        else:
            raise NotImplementedException('{} not implemented yet'.format(layer.__class__))

    def convert_simple_fill_symbol_layer(self, layer: SimpleFillSymbolLayer) -> dict:
        """
        Converts a SimpleFillSymbolLayer
        """
        out = {
            'color': DictionaryConverter.convert_color(layer.color),
            'color_model': layer.color.model,
        }

        if layer.outline_layer:
            out['outline_layer'] = self.convert_symbol_layer(layer.outline_layer)
        if layer.outline_symbol:
            outline_converter = DictionaryConverter()
            out['outline_symbol'] = outline_converter.convert_symbol(layer.outline_symbol)

        return out

    @staticmethod
    def convert_line_symbol_layer(layer: LineSymbolLayer) -> dict:
        """
        Converts a LineSymbolLayer
        """
        if isinstance(layer, SimpleLineSymbolLayer):
            return DictionaryConverter.convert_simple_line_symbol_layer(layer)
        elif isinstance(layer, CartographicLineSymbolLayer):
            return DictionaryConverter.convert_cartographic_line_symbol_layer(layer)
        elif isinstance(layer, MarkerLineSymbolLayer):
            return DictionaryConverter.convert_marker_line_symbol_layer(layer)
        else:
            raise NotImplementedException('{} not implemented yet'.format(layer.__class__))

    @staticmethod
    def convert_decoration(decoration: LineDecoration) -> dict:
        out = {
            'decorations': []
        }
        for d in decoration.decorations:

            decoration_converter = DictionaryConverter()
            if isinstance(d, (LineDecoration)):
                marker_converter = DictionaryConverter()
                out['decorations'].append(marker_converter.convert_decoration(d))
            elif isinstance(d, (SimpleLineDecoration)):
                marker_converter = DictionaryConverter()
                out['decorations'].append(marker_converter.convert_simple_line_decoration(d))
        return out

    @staticmethod
    def convert_simple_line_symbol_layer(layer: SimpleLineSymbolLayer) -> dict:
        """
        Converts a SimpleLineSymbolLayer
        """
        out = {
            'color': DictionaryConverter.convert_color(layer.color),
            'color_model': layer.color.model,
            'width': layer.width,
            'line_type': layer.line_type
        }
        return out

    @staticmethod
    def convert_simple_line_decoration(layer: SimpleLineDecoration) -> dict:
        """
        Converts a SimpleLineDecoration
        """
        out = {
            'fixed_angle': layer.fixed_angle,
            'flip_first': layer.flip_first,
            'flip_all': layer.flip_all,
            'marker': None,
            'positions': layer.marker_positions
        }

        if isinstance(layer.marker, (SymbolLayer)):
            marker_converter = DictionaryConverter()
            out['marker'] = marker_converter.convert_symbol_layer(layer.marker)
        elif isinstance(layer.marker, (Symbol)):
            marker_converter = DictionaryConverter()
            out['marker'] = marker_converter.convert_symbol(layer.marker)

        return out

    @staticmethod
    def convert_template(template: LineTemplate) -> dict:
        """
        Converts a CartographicLineSymbolLayer
        """
        out = {
            'pattern_interval': template.pattern_interval,
            'pattern_parts': template.pattern_parts
        }
        return out

    @staticmethod
    def convert_cartographic_line_symbol_layer(layer: CartographicLineSymbolLayer) -> dict:
        """
        Converts a CartographicLineSymbolLayer
        """
        out = {
            'color': DictionaryConverter.convert_color(layer.color),
            'color_model': layer.color.model,
            'width': layer.width,
            'offset': layer.offset,
            'cap': layer.cap,
            'join': layer.join,
            'template': None,
            'decoration': None
        }
        if layer.template is not None:
            converter = DictionaryConverter()
            out['template'] = converter.convert_template(layer.template)

        if layer.decoration is not None:
            if isinstance(layer.decoration, (LineDecoration)):
                marker_converter = DictionaryConverter()
                out['decoration'] = marker_converter.convert_decoration(layer.decoration)
            elif isinstance(layer.decoration, (SimpleLineDecoration)):
                marker_converter = DictionaryConverter()
                out['decoration'] = marker_converter.convert_simple_line_decoration(layer.decoration)

        return out

    @staticmethod
    def convert_marker_line_symbol_layer(layer: MarkerLineSymbolLayer) -> dict:
        """
        Converts a MarkerLineSymbolLayer
        """
        out = {
            'color': DictionaryConverter.convert_color(layer.color),
            'color_model': layer.color.model if layer.color else None,
            'offset': layer.offset,
            'cap': layer.cap,
            'join': layer.join,
            'template': None,
            'pattern_marker': None,
            'decoration': None
        }
        if layer.template is not None:
            converter = DictionaryConverter()
            out['template'] = converter.convert_template(layer.template)

        if isinstance(layer.pattern_marker, (SymbolLayer)):
            marker_converter = DictionaryConverter()
            out['pattern_marker'] = marker_converter.convert_symbol_layer(layer.pattern_marker)
        elif isinstance(layer.pattern_marker, (Symbol)):
            marker_converter = DictionaryConverter()
            out['pattern_marker'] = marker_converter.convert_symbol(layer.pattern_marker)

        if layer.decoration is not None:
            if isinstance(layer.decoration, (LineDecoration)):
                marker_converter = DictionaryConverter()
                out['decoration'] = marker_converter.convert_decoration(layer.decoration)
            elif isinstance(layer.decoration, (SimpleLineDecoration)):
                marker_converter = DictionaryConverter()
                out['decoration'] = marker_converter.convert_simple_line_decoration(layer.decoration)

        return out

    @staticmethod
    def convert_marker_symbol_layer(layer: MarkerSymbolLayer) -> dict:
        """
        Converts a MarkerSymbolLayer
        """
        if isinstance(layer, SimpleMarkerSymbolLayer):
            return DictionaryConverter.convert_simple_marker_symbol_layer(layer)
        elif isinstance(layer, CharacterMarkerSymbolLayer):
            return DictionaryConverter.convert_character_marker_symbol_layer(layer)
        elif isinstance(layer, ArrowMarkerSymbolLayer):
            return DictionaryConverter.convert_arrow_marker_symbol_layer(layer)
        else:
            raise NotImplementedException('{} not implemented yet'.format(layer.__class__))

    @staticmethod
    def convert_simple_marker_symbol_layer(layer: SimpleMarkerSymbolLayer) -> dict:
        """
        Converts a SimpleMarkerSymbolLayer
        """
        out = {
            'color': DictionaryConverter.convert_color(layer.color),
            'color_model': layer.color.model,
            'marker_type': layer.type,
            'size': layer.size,
            'x_offset': layer.x_offset,
            'y_offset': layer.y_offset,
            'outline_enabled': layer.outline_enabled,
            'outline_color_model': layer.outline_color.model,
            'outline_color': layer.outline_color.to_dict(),
            'outline_size': layer.outline_width
        }
        return out

    @staticmethod
    def convert_character_marker_symbol_layer(layer: CharacterMarkerSymbolLayer) -> dict:
        """
        Converts a CharacterMarkerSymbolLayer
        """
        out = {
            'color': DictionaryConverter.convert_color(layer.color),
            'color_model': layer.color.model,
            'unicode': layer.unicode,
            'font': layer.font,
            'size': layer.size,
            'angle': layer.angle,
            'x_offset': layer.x_offset,
            'y_offset': layer.y_offset
        }
        return out

    @staticmethod
    def convert_arrow_marker_symbol_layer(layer: ArrowMarkerSymbolLayer) -> dict:
        """
        Converts a ArrowMarkerSymbolLayer
        """
        out = {
            'color': DictionaryConverter.convert_color(layer.color),
            'color_model': layer.color.model,
            'size': layer.size,
            'width': layer.width,
            'angle': layer.angle,
            'x_offset': layer.x_offset,
            'y_offset': layer.y_offset
        }
        return out

    @staticmethod
    def convert_color(color) -> dict:
        """
        Converts a color
        """
        return color.to_dict() if color is not None else None
