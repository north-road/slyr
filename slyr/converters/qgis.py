#!/usr/bin/env python

"""
Converts parsed symbol properties to QGIS Symbols
"""

from qgis.core import (QgsUnitTypes,
                       QgsSimpleLineSymbolLayer,
                       QgsSimpleFillSymbolLayer,
                       QgsFillSymbol,
                       QgsLineSymbol,
                       QgsMarkerSymbol,
                       QgsEllipseSymbolLayer,
                       QgsSimpleMarkerSymbolLayer,
                       QgsSimpleMarkerSymbolLayerBase,
                       QgsFontMarkerSymbolLayer,
                       QgsPresetSchemeColorRamp,
                       QgsLimitedRandomColorRamp,
                       QgsGradientColorRamp)
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
from slyr.parser.objects.colors import (
    CMYKColor
)
from slyr.parser.objects.line_symbol_layer import (
    SimpleLineSymbolLayer,
    CartographicLineSymbolLayer,
    LineSymbolLayer)
from slyr.parser.objects.fill_symbol_layer import (
    FillSymbolLayer,
    SimpleFillSymbolLayer,
    ColorSymbol
)
from slyr.parser.objects.marker_symbol_layer import (
    MarkerSymbolLayer,
    SimpleMarkerSymbolLayer,
    ArrowMarkerSymbolLayer,
    CharacterMarkerSymbolLayer
)
from slyr.parser.objects.ramps import (
    ColorRamp,
    AlgorithmicColorRamp,
    PresetColorRamp,
    RandomColorRamp
)
from slyr.converters.converter import NotImplementedException


def symbol_color_to_qcolor(color):
    """
    Converts a symbol color to a QColor
    """
    if isinstance(color, CMYKColor):
        # CMYK color
        return QColor.fromCmykF(color.cyan / 100, color.magenta / 100, color.yellow / 100, color.black / 100)

    return QColor(color.red, color.green, color.blue, 0 if color.is_null else 255)


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

    if isinstance(layer, SimpleFillSymbolLayer):
        if layer.outline_layer:
            if isinstance(layer.outline_layer, (SimpleLineSymbolLayer, CartographicLineSymbolLayer)):
                out.setStrokeColor(symbol_color_to_qcolor(layer.outline_layer.color))
                out.setStrokeWidth(layer.outline_layer.width)
                out.setStrokeWidthUnit(QgsUnitTypes.RenderPoints)
            if isinstance(layer.outline_layer, SimpleLineSymbolLayer):
                out.setStrokeStyle(symbol_pen_to_qpenstyle(layer.outline_layer.line_type))
            if isinstance(layer.outline_layer, CartographicLineSymbolLayer):
                out.setPenJoinStyle(symbol_pen_to_qpenjoinstyle(layer.outline_layer.join))
            # better matching of null stroke color to QGIS symbology
            if out.strokeColor().alpha() == 0:
                out.setStrokeStyle(Qt.NoPen)

            # todo - change to new symbol layer if outline offset, template, etc set
            symbol.appendSymbolLayer(out)
        elif layer.outline_symbol:
            # outline is a symbol itself
            out.setStrokeStyle(Qt.NoPen)
            symbol.appendSymbolLayer(out)

            # get all layers from outline
            append_SymbolLayer_to_QgsSymbolLayer(symbol, layer.outline_symbol)
        else:
            out.setStrokeStyle(Qt.NoPen)
            symbol.appendSymbolLayer(out)
    elif isinstance(layer, ColorSymbol):
        out.setStrokeStyle(Qt.NoPen)
        symbol.appendSymbolLayer(out)


def append_SimpleLineSymbolLayer(symbol, layer):
    """
    Appends a SimpleLineSymbolLayer to a symbol
    """
    color = symbol_color_to_qcolor(layer.color)
    out = QgsSimpleLineSymbolLayer(color)
    out.setEnabled(layer.enabled)
    out.setLocked(layer.locked)
    out.setWidth(layer.width)
    out.setWidthUnit(QgsUnitTypes.RenderPoints)
    out.setPenStyle(symbol_pen_to_qpenstyle(layer.line_type))
    # out.setPenJoinStyle(symbol_pen_to_qpenjoinstyle(layer.join))
    # better matching of null stroke color to QGIS symbology
    if out.color().alpha() == 0:
        out.setPenStyle(Qt.NoPen)

    # todo - change to new symbol layer if outline offset set
    symbol.appendSymbolLayer(out)


def apply_template_to_LineSymbolLayer_custom_dash(template, layer):
    """
    Applies a line template to a QgsSimpleLineSymbolLayer custom dash pattern
    """
    interval = template.pattern_interval

    dash_vector = []
    for part in template.pattern_parts:
        dash_vector.append(part[0] * interval)
        dash_vector.append(part[1] * interval)

    layer.setCustomDashVector(dash_vector)
    layer.setUseCustomDashPattern(True)
    layer.setCustomDashPatternUnit(QgsUnitTypes.RenderPoints)


def append_CartographicLineSymbolLayer(symbol, layer):
    """
    Appends a CartographicLineSymbolLayer to a symbol
    """
    color = symbol_color_to_qcolor(layer.color)
    out = QgsSimpleLineSymbolLayer(color)
    out.setEnabled(layer.enabled)
    out.setLocked(layer.locked)
    out.setWidth(layer.width)
    out.setWidthUnit(QgsUnitTypes.RenderPoints)
    out.setPenJoinStyle(symbol_pen_to_qpenjoinstyle(layer.join))
    out.setPenCapStyle(symbol_pen_to_qpencapstyle(layer.cap))
    if layer.template is not None:
        apply_template_to_LineSymbolLayer_custom_dash(layer.template, out)

    # better matching of null stroke color to QGIS symbology
    if out.color().alpha() == 0:
        out.setPenStyle(Qt.NoPen)

    if layer.decoration is not None:
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


def append_SimpleMarkerSymbolLayer(symbol, layer: SimpleMarkerSymbolLayer):
    """
    Appends a SimpleMarkerSymbolLayer to a symbol
    """
    marker_type = marker_type_to_qgis_type(layer.type)
    out = QgsSimpleMarkerSymbolLayer(marker_type, layer.size)
    out.setSizeUnit(QgsUnitTypes.RenderPoints)

    color = symbol_color_to_qcolor(layer.color)
    if marker_type in ('circle', 'square', 'diamond'):
        out.setColor(color)
    else:
        out.setStrokeColor(color)

    out.setEnabled(layer.enabled)
    out.setLocked(layer.locked)
    out.setOffset(QPointF(layer.x_offset, layer.y_offset))
    out.setOffsetUnit(QgsUnitTypes.RenderPoints)

    if layer.outline_enabled:
        outline_color = symbol_color_to_qcolor(layer.outline_color)
        if marker_type in ('circle', 'square', 'diamond'):
            out.setStrokeColor(outline_color)
            out.setStrokeWidth(layer.outline_width)
            out.setStrokeWidthUnit(QgsUnitTypes.RenderPoints)
        else:
            # for stroke-only symbols, we need to add the outline as an additional
            # symbol layer
            outline_layer = QgsSimpleMarkerSymbolLayer(marker_type, layer.size)
            outline_layer.setSizeUnit(QgsUnitTypes.RenderPoints)
            outline_layer.setStrokeColor(outline_color)
            outline_layer.setStrokeWidth(layer.outline_width)
            outline_layer.setStrokeWidthUnit(QgsUnitTypes.RenderPoints)
            symbol.appendSymbolLayer(outline_layer)

    symbol.appendSymbolLayer(out)


def append_ArrowMarkerSymbolLayer(symbol, layer: ArrowMarkerSymbolLayer):
    """
    Appends a ArrowMarkerSymbolLayer to a symbol
    """
    out = QgsEllipseSymbolLayer()
    out.setSymbolName('triangle')
    out.setStrokeStyle(Qt.NoPen)

    out.setSymbolHeight(layer.size)
    out.setSymbolHeightUnit(QgsUnitTypes.RenderPoints)
    out.setSymbolWidth(layer.width)
    out.setSymbolWidthUnit(QgsUnitTypes.RenderPoints)

    color = symbol_color_to_qcolor(layer.color)
    out.setColor(color)
    out.setStrokeColor(color)  # why not, makes the symbol a bit easier to modify in qgis

    # TODO -- confirm whether ArcGIS has same offset/rotation linkages as QGIS does!
    out.setOffset(QPointF(layer.x_offset, layer.y_offset))
    out.setOffsetUnit(QgsUnitTypes.RenderPoints)
    out.setAngle(360 - layer.angle)

    out.setEnabled(layer.enabled)
    out.setLocked(layer.locked)

    symbol.appendSymbolLayer(out)


def append_CharacterMarkerSymbolLayer(symbol, layer):
    """
    Appends a CharacterMarkerSymbolLayer to a symbol
    """
    font_family = layer.font
    character = chr(layer.unicode)
    color = symbol_color_to_qcolor(layer.color)
    angle = 360 - layer.angle

    out = QgsFontMarkerSymbolLayer(font_family, character, layer.size, color, angle)
    out.setSizeUnit(QgsUnitTypes.RenderPoints)

    # TODO
    # out.setEnabled(layer.enabled)
    out.setLocked(layer.locked)
    out.setOffset(QPointF(layer.x_offset, layer.y_offset))
    out.setOffsetUnit(QgsUnitTypes.RenderPoints)

    symbol.appendSymbolLayer(out)


def append_FillSymbolLayer(symbol, layer):
    """
    Appends a FillSymbolLayer to a symbol
    """
    if isinstance(layer, (SimpleFillSymbolLayer, ColorSymbol)):
        append_SimpleFillSymbolLayer(symbol, layer)
    else:
        raise NotImplementedException('Converting {} not implemented yet'.format(layer.__class__.__name__))


def append_LineSymbolLayer(symbol, layer):
    """
    Appends a LineSymbolLayer to a QgsSymbol
    """
    if isinstance(layer, SimpleLineSymbolLayer):
        append_SimpleLineSymbolLayer(symbol, layer)
    elif isinstance(layer, CartographicLineSymbolLayer):
        append_CartographicLineSymbolLayer(symbol, layer)
    else:
        raise NotImplementedException('Converting {} not implemented yet'.format(layer.__class__.__name__))


def append_MarkerSymbolLayer(symbol, layer):
    """
    Appends a MarkerSymbolLayer to a QgsSymbol
    """
    if isinstance(layer, SimpleMarkerSymbolLayer):
        append_SimpleMarkerSymbolLayer(symbol, layer)
    elif isinstance(layer, ArrowMarkerSymbolLayer):
        append_ArrowMarkerSymbolLayer(symbol, layer)
    elif isinstance(layer, CharacterMarkerSymbolLayer):
        append_CharacterMarkerSymbolLayer(symbol, layer)
    else:
        raise NotImplementedException('Converting {} not implemented yet'.format(layer.__class__.__name__))


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
            raise NotImplementedException('Converting {} not implemented yet'.format(layer.__class__.__name__))
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


def ColorRamp_to_QgsColorRamp(ramp: ColorRamp):
    """
    Converts a ColorRamp to a QgsColorRamp
    """
    if isinstance(ramp, PresetColorRamp):
        return PresetColorRamp_to_QgsColorRamp(ramp)
    elif isinstance(ramp, RandomColorRamp):
        return RandomColorRamp_to_QgsColorRamp(ramp)
    elif isinstance(ramp, AlgorithmicColorRamp):
        return AlgorithmicColorRamp_to_QgsColorRamp(ramp)
    else:
        raise NotImplementedException('Converting {} not implemented yet'.format(ramp.__class__.__name__))


def PresetColorRamp_to_QgsColorRamp(ramp: PresetColorRamp):
    """
    Converts a PresetColorRamp to a QgsColorRamp
    """
    colors = [symbol_color_to_qcolor(c) for c in ramp.colors]
    out = QgsPresetSchemeColorRamp(colors)
    return out


def RandomColorRamp_to_QgsColorRamp(ramp: RandomColorRamp):
    """
    Converts a RandomColorRamp to a QgsColorRamp
    """

    def fix_range(val):
        # Saturation/values range from 0-100 in esri symbols, 0-255 in qgis
        return 255 * val / 100

    # TODO - how to correctly handle color count option?
    out = QgsLimitedRandomColorRamp(count=100,
                                    hueMax=ramp.hue_max, hueMin=ramp.hue_min,
                                    satMax=fix_range(ramp.sat_max), satMin=fix_range(ramp.sat_min),
                                    valMax=fix_range(ramp.val_max), valMin=fix_range(ramp.val_min))
    return out


def AlgorithmicColorRamp_to_QgsColorRamp(ramp: AlgorithmicColorRamp):
    """
    Converts a AlgorithmicColorRamp to a QgsColorRamp
    """
    out = QgsGradientColorRamp(symbol_color_to_qcolor(ramp.color1),
                               symbol_color_to_qcolor(ramp.color2))
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
                raise NotImplementedException('Marker halos are not yet supported')
        except AttributeError:
            pass
    elif issubclass(symbol.__class__, ColorRamp):
        out = ColorRamp_to_QgsColorRamp(symbol)
        return out
    else:
        raise NotImplementedException()

    add_symbol_layers(out, symbol)

    return out
