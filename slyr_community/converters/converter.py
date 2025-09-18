#!/usr/bin/env python

# /***************************************************************************
# color_ramp.py
# ----------
# Date                 : October 2019
# copyright            : (C) 2019 by Nyall Dawson
# email                : nyall.dawson@gmail.com
#
#  ***************************************************************************/
#
# /***************************************************************************
#  *                                                                         *
#  *   This program is free software; you can redistribute it and/or modify  *
#  *   it under the terms of the GNU General Public License as published by  *
#  *   the Free Software Foundation; either version 2 of the License, or     *
#  *   (at your option) any later version.                                   *
#  *                                                                         *
#  ***************************************************************************/

"""
Base class for converters
"""

from typing import Union
from ..parser.objects.multi_layer_symbols import (
    MultiLayerSymbol,
    MultiLayerFillSymbol,
    MultiLayerLineSymbol,
    MultiLayerMarkerSymbol,
)
from ..parser.exceptions import NotImplementedException
from ..parser.objects.symbol_layer import SymbolLayer
from ..parser.objects.line_symbol_layer import LineSymbolLayer
from ..parser.objects.fill_symbol_layer import FillSymbolLayer
from ..parser.objects.marker_symbol_layer import MarkerSymbolLayer
from ..parser.objects.ramps import ColorRamp


class Converter:
    """
    Base class for symbol Converters
    """

    def convert_symbol(self, symbol: MultiLayerSymbol):
        """
        Converts a symbol.
        :param symbol: symbol to convert
        """
        if issubclass(symbol.__class__, (MultiLayerFillSymbol, FillSymbolLayer)):
            self.convert_fill_symbol(symbol)
        elif issubclass(symbol.__class__, (MultiLayerLineSymbol, LineSymbolLayer)):
            self.convert_line_symbol(symbol)
        elif issubclass(symbol.__class__, (MarkerSymbolLayer, MultiLayerMarkerSymbol)):
            self.convert_marker_symbol(symbol)
        elif issubclass(symbol.__class__, ColorRamp):
            self.convert_color_ramp(symbol)
        else:
            raise NotImplementedException(str(symbol.__class__))

    def convert_fill_symbol(self, symbol: Union[SymbolLayer, MultiLayerFillSymbol]):  # pylint: disable=unused-argument
        """
        Converts a FillSymbol
        """
        raise NotImplementedException("Fill symbol conversion not implemented")

    def convert_line_symbol(self, symbol: Union[SymbolLayer, MultiLayerLineSymbol]):  # pylint: disable=unused-argument
        """
        Converts a LineSymbol
        """
        raise NotImplementedException("Line symbol conversion not implemented")

    def convert_marker_symbol(self, symbol: Union[SymbolLayer, MultiLayerMarkerSymbol]):  # pylint: disable=unused-argument
        """
        Converts a MarkerSymbol
        """
        raise NotImplementedException("Marker symbol conversion not implemented")

    def convert_color_ramp(self, ramp: ColorRamp):  # pylint: disable=unused-argument
        """
        Converts a color ramp
        """
        raise NotImplementedException("Color ramp conversion not implemented")
