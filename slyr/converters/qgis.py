#!/usr/bin/env python

"""
Converts parsed symbol properties to QGIS Symbols
"""

from qgis.core import (QgsSimpleLineSymbolLayer,
                       QgsSimpleFillSymbolLayer,
                       QgsFillSymbol,
                       QgsLineSymbol,
                       QgsMarkerSymbol,
                       QgsSimpleMarkerSymbolLayer,
                       QgsSimpleMarkerSymbolLayerBase,
                       QgsFontMarkerSymbolLayer)
from qgis.PyQt.QtCore import (Qt, QPointF)
from qgis.PyQt.QtGui import (QColor)

from slyr.parser.symbol_parser import (
    FillSymbol,
    LineSymbol,
    MarkerSymbol
)
from slyr.parser.objects.symbol_layer import (
    SymbolLayer
)
from slyr.parser.objects.line_symbol_layer import (
    SimpleLineSymbolLayer,
    CartographicLineSymbolLayer,
    LineSymbolLayer)
from slyr.parser.objects.fill_symbol_layer import (
    FillSymbolLayer,
    SimpleFillSymbolLayer
)
from slyr.parser.objects.marker_symbol_layer import (
    MarkerSymbolLayer,
    SimpleMarkerSymbolLayer,
    CharacterMarkerSymbolLayer
)
from slyr.converters.converter import NotImplementedException


def symbol_color_to_qcolor(color):
    """
    Converts a symbol color to a QColor
    """
    if 'C' in color:
        # CMYK color
        return QColor.fromCmykF(color['C'] / 100, color['M'] / 100, color['Y'] / 100, color['K'] / 100)

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
    # out.setPenJoinStyle(symbol_pen_to_qpenjoinstyle(layer.join))
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
        interval = layer.pattern_interval

        dash_vector = []
        for part in layer.pattern_parts:
            dash_vector.append(points_to_mm(part[0] * interval))
            dash_vector.append(points_to_mm(part[1] * interval))

        out.setCustomDashVector(dash_vector)
        out.setUseCustomDashPattern(True)

    # better matching of null stroke color to QGIS symbology
    if out.color().alpha() == 0:
        out.setPenStyle(Qt.NoPen)

    if layer.marker_positions or layer.marker:
        raise NotImplementedException('Cartographic line start/end markers are not yet supported')

    # todo - change to new symbol layer if outline offset set
    symbol.appendSymbolLayer(out)


def marker_type_to_qgis_type(marker_type):
    """
    Converts simple marker types to corresponding QGIS types
    """
    if marker_type == 'circle':
        return QgsSimpleMarkerSymbolLayerBase.Circle
    elif marker_type == 'square':
        return QgsSimpleMarkerSymbolLayerBase.Square
    elif marker_type == 'cross':
        return QgsSimpleMarkerSymbolLayerBase.Cross
    elif marker_type == 'x':
        return QgsSimpleMarkerSymbolLayerBase.Cross2
    elif marker_type == 'diamond':
        return QgsSimpleMarkerSymbolLayerBase.Diamond
    else:
        raise NotImplementedException('Marker type {} not implemented'.format(marker_type))


def append_SimpleMarkerSymbolLayer(symbol, layer):
    """
    Appends a SimpleMarkerSymbolLayer to a symbol
    """
    marker_type = marker_type_to_qgis_type(layer.type)
    size = points_to_mm(layer.size)
    out = QgsSimpleMarkerSymbolLayer(marker_type, size)

    color = symbol_color_to_qcolor(layer.color)
    if marker_type in ('circle', 'square', 'diamond'):
        out.setColor(color)
    else:
        out.setStrokeColor(color)

    out.setEnabled(layer.enabled)
    out.setLocked(layer.locked)
    out.setOffset(QPointF(points_to_mm(layer.x_offset), points_to_mm(layer.y_offset)))

    if layer.outline_enabled:
        outline_color = symbol_color_to_qcolor(layer.outline_color)
        if marker_type in ('circle', 'square', 'diamond'):
            out.setStrokeColor(outline_color)
            out.setStrokeWidth(points_to_mm(layer.outline_width))
        else:
            # for stroke-only symbols, we need to add the outline as an additional
            # symbol layer
            outline_layer = QgsSimpleMarkerSymbolLayer(marker_type, size)
            outline_layer.setStrokeColor(outline_color)
            outline_layer.setStrokeWidth(points_to_mm(layer.outline_width))
            symbol.appendSymbolLayer(outline_layer)

    symbol.appendSymbolLayer(out)


def append_CharacterMarkerSymbolLayer(symbol, layer):
    """
    Appends a CharacterMarkerSymbolLayer to a symbol
    """
    font_family = layer.font
    character = chr(layer.unicode)
    size = points_to_mm(layer.size)
    color = symbol_color_to_qcolor(layer.color)
    angle = 360 - layer.angle

    out = QgsFontMarkerSymbolLayer(font_family, character, size, color, angle)

    # TODO
    # out.setEnabled(layer.enabled)
    out.setLocked(layer.locked)
    out.setOffset(QPointF(points_to_mm(layer.x_offset), points_to_mm(layer.y_offset)))

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


def append_MarkerSymbolLayer(symbol, layer):
    """
    Appends a MarkerSymbolLayer to a QgsSymbol
    """
    if isinstance(layer, SimpleMarkerSymbolLayer):
        append_SimpleMarkerSymbolLayer(symbol, layer)
    elif isinstance(layer, CharacterMarkerSymbolLayer):
        append_CharacterMarkerSymbolLayer(symbol, layer)
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
        elif issubclass(layer.__class__, MarkerSymbolLayer):
            append_MarkerSymbolLayer(symbol, layer)
        else:
            raise NotImplementedException('{} not implemented yet'.format(layer.__class__))
    else:
        for l in layer.levels:
            append_SymbolLayer_to_QgsSymbolLayer(symbol, l)


def add_symbol_layers(out, symbol):
    """
    Adds all symbol layers to a symbol
    """
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
        out = QgsFillSymbol()
    elif issubclass(symbol.__class__, (LineSymbol, LineSymbolLayer)):
        out = QgsLineSymbol()
    elif issubclass(symbol.__class__, (MarkerSymbol, MarkerSymbolLayer)):
        out = QgsMarkerSymbol()
        try:
            if symbol.halo:
                raise NotImplementedException('Mark halos are not yet supported')
        except AttributeError:
            pass
    else:
        raise NotImplementedException()

    add_symbol_layers(out, symbol)

    return out
