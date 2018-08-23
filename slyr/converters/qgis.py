#!/usr/bin/env python

"""
Converts parsed symbol properties to QGIS Symbols
"""

from qgis.core import (QgsSimpleLineSymbolLayer,
                       QgsSimpleFillSymbolLayer,
                       QgsFillSymbol)
from qgis.PyQt.QtCore import (Qt)
from qgis.PyQt.QtGui import (QColor)

from slyr.parser.symbol_parser import (
    SimpleLineSymbolLayer,
    CartographicLineSymbolLayer,
    FillSymbolLayer,
    SimpleFillSymbolLayer,
    SymbolLayer
)


class NotImplementedException(Exception):
    """
    Raised when a symbol type or symbol layer type is not yet implemented in the converter
    """
    pass


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


def SimpleLineSymbolLayer_to_QgsSimpleLineSymbolLayer(layer):
    """
    Converts a simple line symbol layer to a QgsSimpleLineSymbolLayer
    """
    out = QgsSimpleLineSymbolLayer(
        symbol_color_to_qcolor(layer.color),
        points_to_mm(layer.width),
        symbol_pen_to_qpenstyle(layer.line_type)
    )

    # better mapping of "null" colors to QGIS symbology
    if out.color().alpha() == 0:
        out.setPenStyle(Qt.NoPen)
    return out


def CartographicLineSymbolLayer_to_QgsSimpleLineSymbolLayer(layer):
    """
    Converts a cartographic line symbol layer to a QgsSimpleLineSymbolLayer
    """
    out = QgsSimpleLineSymbolLayer(
        symbol_color_to_qcolor(layer.color),
        points_to_mm(layer.width),
        symbol_pen_to_qpenstyle(layer.line_type)
    )
    out.setPenCapStyle(symbol_pen_to_qpencapstyle(layer.cap))
    out.setPenJoinStyle(symbol_pen_to_qpenjoinstyle(layer.join))
    out.setOffset(points_to_mm(layer.offset))
    return out


def SimpleFillSymbolLayer_to_QgsSimpleFillSymbolLayer(layer):
    """
    Converts a SimpleFillSymbolLayer to a QgsSimpleFillSymbolLayer
    """
    fill_color = symbol_color_to_qcolor(layer.color)
    out = QgsSimpleFillSymbolLayer(fill_color)

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
    else:
        # todo - outline symbol layer
        raise NotImplementedException('Outline symbol layer not implemented')

    return out


def FillSymbolLayer_to_QgsFillSymbolLayer(layer):
    """
    Converts a FillSymbolLayer to a QgsFillSymbolLayer
    """
    if isinstance(layer, SimpleFillSymbolLayer):
        return SimpleFillSymbolLayer_to_QgsSimpleFillSymbolLayer(layer)
    else:
        raise NotImplementedException('{} not implemented yet'.format(layer.__class__))


def SymbolLayer_to_QgsSymbolLayer(layer):
    """
    Converts a SymbolLayer to a QgsSymbolLayer
    """
    if issubclass(layer.__class__, FillSymbolLayer):
        out = FillSymbolLayer_to_QgsFillSymbolLayer(layer)
    else:
        raise NotImplementedException('{} not implemented yet'.format(layer.__class__))
    out.setEnabled(layer.enabled)
    out.setLocked(layer.locked)
    return out


def FillSymbol_to_QgsFillSymbol(symbol):
    """
    Converts a FillSymbol to a QgsFillSymbol
    """
    out = QgsFillSymbol()
    if issubclass(symbol.__class__, SymbolLayer):
        new_layer = SymbolLayer_to_QgsSymbolLayer(symbol)
        out.changeSymbolLayer(0, new_layer)
    else:
        out.changeSymbolLayer(0, SymbolLayer_to_QgsSymbolLayer(symbol.levels[0]))
        for l in symbol.levels[1:]:
            out.appendSymbolLayer(SymbolLayer_to_QgsSymbolLayer(l))
    return out
