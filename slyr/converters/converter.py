#!/usr/bin/env python

"""
Base class for converters
"""

from typing import Union
from slyr.parser.symbol_parser import (
    Symbol,
    FillSymbol,
    LineSymbol,
    MarkerSymbol,
)
from slyr.parser.objects.symbol_layer import SymbolLayer
from slyr.parser.objects.line_symbol_layer import LineSymbolLayer
from slyr.parser.objects.fill_symbol_layer import FillSymbolLayer
from slyr.parser.objects.marker_symbol_layer import MarkerSymbolLayer


class NotImplementedException(Exception):
    """
    Raised when a symbol type or symbol layer type is not yet implemented in the converter
    """
    pass


class Converter:
    """
    Base class for symbol Converters
    """

    def convert_symbol(self, symbol: Symbol):
        """
        Converts a symbol.
        :param symbol: symbol to convert
        """
        if issubclass(symbol.__class__, (FillSymbolLayer, FillSymbol)):
            self.convert_fill_symbol(symbol)
        elif issubclass(symbol.__class__, (LineSymbolLayer, LineSymbol)):
            self.convert_line_symbol(symbol)
        elif issubclass(symbol.__class__, (MarkerSymbolLayer, MarkerSymbol)):
            self.convert_marker_symbol(symbol)
        else:
            raise NotImplementedException(str(symbol.__class__))

    def convert_fill_symbol(self, symbol: Union[SymbolLayer, FillSymbol]):  # pylint: disable=unused-argument
        """
        Converts a FillSymbol
        """
        raise NotImplementedException('Fill symbol conversion not implemented')

    def convert_line_symbol(self, symbol: Union[SymbolLayer, LineSymbol]):  # pylint: disable=unused-argument
        """
        Converts a LineSymbol
        """
        raise NotImplementedException('Line symbol conversion not implemented')

    def convert_marker_symbol(self, symbol: Union[SymbolLayer, MarkerSymbol]):  # pylint: disable=unused-argument
        """
        Converts a MarkerSymbol
        """
        raise NotImplementedException('Marker symbol conversion not implemented')
