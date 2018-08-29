#!/usr/bin/env python

"""
Converts parsed symbol properties to QGIS Symbols
"""

from qgis.core import (QgsSimpleLineSymbolLayer,
                       QgsSimpleFillSymbolLayer,
                       QgsFillSymbol,
                       QgsLineSymbol,
                       QgsMarkerSymbol)
from qgis.PyQt.QtCore import (Qt)
from qgis.PyQt.QtGui import (QColor)

from slyr.parser.symbol_parser import (
    SimpleLineSymbolLayer,
    CartographicLineSymbolLayer,
    FillSymbolLayer,
    SimpleFillSymbolLayer,
    SymbolLayer,
    LineSymbolLayer,
    FillSymbol,
    LineSymbol,
    MarkerSymbol,
    MarkerSymbolLayer
)

from slyr.converters.converter import NotImplementedException


def symbol_color_to_qcolor(color):
    """
    Converts a symbol color to a QColor
    """
    return QColor(color['R'], color['G'], color['B'], 0 if color['is_null'] else 255)


def points_to_mm(points):
    """
    Converts a point size to mm
    """
    return points * 0.352778


def symbol_pen_to_qpenstyle(style):
    """
    Converts a symbol pen style to a QPenStyle
    """
    types = {
        'solid': Qt.SolidLine,
        'dashed': Qt.DashLine,
        'dotted': Qt.DotLine,
        'dash dot': Qt.DashDotLine,
        'dash dot dot': Qt.DashDotDotLine,
        'null': Qt.NoPen
    }
    return types[style]


def symbol_pen_to_qpencapstyle(style):
    """
    Converts a symbol pen cap to a QPenCapStyle
    """
    types = {
        'butt': Qt.FlatCap,
        'round': Qt.RoundCap,
        'square': Qt.SquareCap
    }
    return types[style]


def symbol_pen_to_qpenjoinstyle(style):
    """
    Converts a symbol pen join to a QPenJoinStyle
    """
    types = {
        'miter': Qt.MiterJoin,
        'round': Qt.RoundJoin,
        'bevel': Qt.BevelJoin
    }
    return types[style]


def append_SimpleFillSymbolLayer(symbol, layer):
    """
    Appends a SimpleFillSymbolLayer to a symbol
    """
    fill_color = symbol_color_to_qcolor(layer.color)
    out = QgsSimpleFillSymbolLayer(fill_color)
    out.setEnabled(layer.enabled)
    out.setLocked(layer.locked)

    if layer.outline_layer:
        if isinstance(layer.outline_layer, (SimpleLineSymbolLayer, CartographicLineSymbolLayer)):
            out.setStrokeColor(symbol_color_to_qcolor(layer.outline_layer.color))
            out.setStrokeWidth(points_to_mm(layer.outline_layer.width))
        if isinstance(layer.outline_layer, SimpleLineSymbolLayer):
            out.setStrokeStyle(symbol_pen_to_qpenstyle(layer.outline_layer.line_type))
        if isinstance(layer.outline_layer, CartographicLineSymbolLayer):
            out.setPenJoinStyle(symbol_pen_to_qpenjoinstyle(layer.outline_layer.join))
        # better matching of null stroke color to QGIS symbology
        if out.strokeColor().alpha() == 0:
            out.setStrokeStyle(Qt.NoPen)

        # todo - change to new symbol layer if outline offset set
        symbol.appendSymbolLayer(out)
    else:
        # outline is a symbol itself
        out.setStrokeStyle(Qt.NoPen)
        symbol.appendSymbolLayer(out)

        # get all layers from outline
        append_SymbolLayer_to_QgsSymbolLayer(symbol, layer.outline_symbol)


def append_SimpleLineSymbolLayer(symbol, layer):
    """
    Appends a SimpleLineSymbolLayer to a symbol
    """
    color = symbol_color_to_qcolor(layer.color)
    out = QgsSimpleLineSymbolLayer(color)
    out.setEnabled(layer.enabled)
    out.setLocked(layer.locked)
    out.setWidth(points_to_mm(layer.width))
    out.setPenStyle(symbol_pen_to_qpenstyle(layer.line_type))
    #out.setPenJoinStyle(symbol_pen_to_qpenjoinstyle(layer.join))
    # better matching of null stroke color to QGIS symbology
    if out.color().alpha() == 0:
        out.setPenStyle(Qt.NoPen)

    # todo - change to new symbol layer if outline offset set
    symbol.appendSymbolLayer(out)

def append_CartographicLineSymbolLayer(symbol, layer):
    """
    Appends a CartographicLineSymbolLayer to a symbol
    """
    color = symbol_color_to_qcolor(layer.color)
    out = QgsSimpleLineSymbolLayer(color)
    out.setEnabled(layer.enabled)
    out.setLocked(layer.locked)
    out.setWidth(points_to_mm(layer.width))
    out.setPenJoinStyle(symbol_pen_to_qpenjoinstyle(layer.join))
    out.setPenCapStyle(symbol_pen_to_qpencapstyle(layer.cap))
    if layer.pattern_parts:
        raise NotImplementedException('Cartographic line patterns not implemented yet')

    # better matching of null stroke color to QGIS symbology
    if out.color().alpha() == 0:
        out.setPenStyle(Qt.NoPen)

    # todo - change to new symbol layer if outline offset set
    symbol.appendSymbolLayer(out)

def append_FillSymbolLayer(symbol, layer):
    """
    Appends a FillSymbolLayer to a symbol
    """
    if isinstance(layer, SimpleFillSymbolLayer):
        append_SimpleFillSymbolLayer(symbol, layer)
    else:
        raise NotImplementedException('{} not implemented yet'.format(layer.__class__))


def append_LineSymbolLayer(symbol, layer):
    """
    Appends a LineSymbolLayer to a QgsSymbol
    """
    if isinstance(layer, SimpleLineSymbolLayer):
        append_SimpleLineSymbolLayer(symbol, layer)
    elif isinstance(layer, CartographicLineSymbolLayer):
        append_CartographicLineSymbolLayer(symbol, layer)
    else:
        raise NotImplementedException('{} not implemented yet'.format(layer.__class__))


def append_SymbolLayer_to_QgsSymbolLayer(symbol, layer):
    """
    Appends a SymbolLayer to a QgsSymbolLayer
    """
    if issubclass(layer.__class__, SymbolLayer):
        if issubclass(layer.__class__, FillSymbolLayer):
            append_FillSymbolLayer(symbol, layer)
        elif issubclass(layer.__class__, LineSymbolLayer):
            append_LineSymbolLayer(symbol, layer)
        else:
            raise NotImplementedException('{} not implemented yet'.format(layer.__class__))
    else:
        for l in layer.levels:
            append_SymbolLayer_to_QgsSymbolLayer(symbol, l)

def FillSymbol_to_QgsFillSymbol(symbol):
    """
    Converts a FillSymbol to a QgsFillSymbol
    """
    out = QgsFillSymbol()
    out.deleteSymbolLayer(0)
    if issubclass(symbol.__class__, SymbolLayer):
        append_SymbolLayer_to_QgsSymbolLayer(out, symbol)
    else:
        for l in symbol.levels:
            append_SymbolLayer_to_QgsSymbolLayer(out, l)
    return out


def Symbol_to_QgsSymbol(symbol):
    """
    Converts a raw Symbol to a QgsSymbol
    """
    if issubclass(symbol.__class__, (FillSymbol, FillSymbolLayer)):
        out = FillSymbol_to_QgsFillSymbol(symbol)
    elif issubclass(symbol.__class__, (LineSymbol, LineSymbolLayer)):
        out = QgsLineSymbol()
        raise NotImplementedException()
    elif issubclass(symbol.__class__, (MarkerSymbol, MarkerSymbolLayer)):
        out = QgsMarkerSymbol()
        raise NotImplementedException()
    else:
        raise NotImplementedException()

    return out
