#!/usr/bin/env python

"""
Converts parsed symbol properties to QGIS Symbols
"""

import base64
import os
import subprocess
from qgis.core import (QgsUnitTypes,
                       QgsSimpleLineSymbolLayer,
                       QgsSimpleFillSymbolLayer,
                       QgsFillSymbol,
                       QgsLineSymbol,
                       QgsMarkerSymbol,
                       QgsEllipseSymbolLayer,
                       QgsSimpleMarkerSymbolLayer,
                       QgsSvgMarkerSymbolLayer,
                       QgsSimpleMarkerSymbolLayerBase,
                       QgsFontMarkerSymbolLayer,
                       QgsPresetSchemeColorRamp,
                       QgsLimitedRandomColorRamp,
                       QgsGradientColorRamp,
                       QgsMarkerLineSymbolLayer,
                       QgsLinePatternFillSymbolLayer,
                       QgsPointPatternFillSymbolLayer,
                       QgsRasterFillSymbolLayer,
                       QgsSVGFillSymbolLayer)
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
from slyr.parser.objects.picture import (
    EmfPicture,
    StdPicture
)
from slyr.parser.objects.decoration import (
    LineDecoration
)
from slyr.parser.objects.line_symbol_layer import (
    SimpleLineSymbolLayer,
    CartographicLineSymbolLayer,
    MarkerLineSymbolLayer,
    HashLineSymbolLayer,
    LineSymbolLayer)
from slyr.parser.objects.fill_symbol_layer import (
    FillSymbolLayer,
    SimpleFillSymbolLayer,
    ColorSymbol,
    LineFillSymbolLayer,
    MarkerFillSymbolLayer,
    PictureFillSymbolLayer
)
from slyr.parser.objects.marker_symbol_layer import (
    MarkerSymbolLayer,
    SimpleMarkerSymbolLayer,
    ArrowMarkerSymbolLayer,
    CharacterMarkerSymbolLayer,
    PictureMarkerSymbolLayer
)
from slyr.parser.objects.ramps import (
    ColorRamp,
    AlgorithmicColorRamp,
    PresetColorRamp,
    RandomColorRamp
)
from slyr.converters.converter import NotImplementedException
from slyr.parser.pictures import PictureUtils


class Context:
    """
    Symbol conversion context
    """

    def __init__(self):
        self.symbol_name = ''
        self.picture_folder = ''
        self.embed_pictures = True


def convert_angle(angle: float) -> float:
    """
    Converts an ESRI angle (counter-clockwise) to a QGIS angle (clockwise)
    """
    a = 360 - angle
    if a > 180:
        # instead of "359", use "-1"
        a -= 360
    return a


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


def append_SimpleFillSymbolLayer(symbol, layer: SimpleFillSymbolLayer, context: Context):
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
            append_SymbolLayer_to_QgsSymbolLayer(symbol, layer.outline_symbol, context)
        else:
            out.setStrokeStyle(Qt.NoPen)
            symbol.appendSymbolLayer(out)
    elif isinstance(layer, ColorSymbol):
        out.setStrokeStyle(Qt.NoPen)
        symbol.appendSymbolLayer(out)


def append_LineFillSymbolLayer(symbol, layer: LineFillSymbolLayer, context: Context):
    """
    Appends a LineFillSymbolLayer to a symbol
    """
    line = Symbol_to_QgsSymbol(layer.line, context.symbol_name, context.picture_folder, context.embed_pictures)

    out = QgsLinePatternFillSymbolLayer()
    out.setSubSymbol(line)
    out.setLineAngle(convert_angle(layer.angle))
    out.setDistance(layer.separation)
    out.setDistanceUnit(QgsUnitTypes.RenderPoints)
    out.setOffset(layer.offset)
    out.setOffsetUnit(QgsUnitTypes.RenderPoints)

    symbol.appendSymbolLayer(out)
    if layer.outline_layer:
        append_SymbolLayer_to_QgsSymbolLayer(symbol, layer.outline_layer, context)
    elif layer.outline_symbol:
        # get all layers from outline
        append_SymbolLayer_to_QgsSymbolLayer(symbol, layer.outline_symbol, context)


def append_MarkerFillSymbolLayer(symbol, layer: MarkerFillSymbolLayer, context: Context):
    """
    Appends a MarkerFillSymbolLayer to a symbol
    """
    marker = Symbol_to_QgsSymbol(layer.marker, context.symbol_name, context.picture_folder, context.embed_pictures)

    out = QgsPointPatternFillSymbolLayer()
    out.setSubSymbol(marker)

    out.setDistanceX(layer.separation_x)
    out.setDistanceXUnit(QgsUnitTypes.RenderPoints)
    out.setDistanceY(layer.separation_y)
    out.setDistanceYUnit(QgsUnitTypes.RenderPoints)

    # Offset is not supported - displacement in QGIS has a different meaning!
    # out.setDisplacementX(layer.offset_x)
    # out.setDisplacementXUnit(QgsUnitTypes.RenderPoints)
    # out.setDisplacementY(layer.offset_y)
    # out.setDisplacementYUnit(QgsUnitTypes.RenderPoints)

    symbol.appendSymbolLayer(out)
    if layer.outline_layer:
        append_SymbolLayer_to_QgsSymbolLayer(symbol, layer.outline_layer, context)
    elif layer.outline_symbol:
        # get all layers from outline
        append_SymbolLayer_to_QgsSymbolLayer(symbol, layer.outline_symbol, context)


def write_picture(picture, symbol_name: str, picture_folder: str, fg, bg, trans):
    """
    Writes a picture binary content to a file, converting raster colors if necessary
    """
    if issubclass(picture.__class__, StdPicture):
        picture = picture.picture
    fg_color = symbol_color_to_qcolor(fg) if fg else None
    bg_color = symbol_color_to_qcolor(bg) if bg else None
    trans_color = symbol_color_to_qcolor(trans) if trans else None
    new_content = PictureUtils.set_colors(picture.content, fg_color, bg_color, trans_color)
    path = os.path.join(picture_folder, symbol_name + '.png')
    PictureUtils.to_png(new_content, path)
    return path


def write_svg(content: str, symbol_name: str, picture_folder: str):
    """
    Writes a picture binary content to an SVG file
    """
    path = os.path.join(picture_folder, symbol_name + '.svg')
    with open(path, 'wt') as f:
        f.write(content)
    return path


def emf_to_svg(emf_path: str, svg_path: str, inkscape_path: str = None):
    """
    Converts an EMF file to an SVG file (using inkscape)
    """
    binary = 'inkscape'
    if inkscape_path is not None:
        binary = os.path.join(inkscape_path, binary)

    export_args = [binary,
                   '--file',
                   emf_path,
                   '--export-plain-svg',
                   svg_path]

    print(' '.join(export_args))

    CREATE_NO_WINDOW = 0x08000000
    try:
        _ = subprocess.run(export_args, stdout=subprocess.PIPE, creationflags=CREATE_NO_WINDOW)
    except ValueError:
        _ = subprocess.run(export_args, stdout=subprocess.PIPE)


def append_PictureFillSymbolLayer(symbol, layer: PictureFillSymbolLayer, context: Context):
    """
    Appends a PictureFillSymbolLayer to a symbol
    """
    picture = layer.picture
    if issubclass(picture.__class__, StdPicture):
        picture = picture.picture

    if issubclass(picture.__class__, EmfPicture):
        path = os.path.join(context.picture_folder, context.symbol_name + '.emf')
        with open(path, 'wb') as f:
            f.write(picture.content)

        svg_path = os.path.join(context.picture_folder, context.symbol_name + '.svg')
        emf_to_svg(path, svg_path)

        #        out = QgsSVGFillSymbolLayer(svg_path)
        raise NotImplementedException('EMF Picture fills not supported yet')

    # use raster fill
    image_path = write_picture(picture, context.symbol_name, context.picture_folder,
                               layer.color_foreground,
                               layer.color_background,
                               layer.color_transparent)

    out = QgsRasterFillSymbolLayer(image_path)

    # TODO - maybe we want to convert to points/mm so print layouts work nicely
    out.setWidth(layer.scale_x * PictureUtils.width_pixels(picture.content))
    out.setWidthUnit(QgsUnitTypes.RenderPixels)

    out.setAngle(convert_angle(layer.angle))

    symbol.appendSymbolLayer(out)
    if layer.outline_layer:
        append_SymbolLayer_to_QgsSymbolLayer(symbol, layer.outline_layer, context)
    elif layer.outline_symbol:
        # get all layers from outline
        append_SymbolLayer_to_QgsSymbolLayer(symbol, layer.outline_symbol, context)


def append_SimpleLineSymbolLayer(symbol, layer, context: Context):  # pylint: disable=unused-argument
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
    if not template.pattern_parts:
        return

    interval = template.pattern_interval

    dash_vector = []
    for part in template.pattern_parts:
        if part[0] == 0:
            # QGIS skips drawing a 0 part, so fake it
            dash_vector.append(0.000001 * interval)
        else:
            dash_vector.append(part[0] * interval)

        if part[1] == 0:
            # QGIS skips drawing a 0 part, so fake it
            dash_vector.append(0.000001 * interval)
        else:
            dash_vector.append(part[1] * interval)

    layer.setCustomDashVector(dash_vector)
    layer.setUseCustomDashPattern(True)
    layer.setCustomDashPatternUnit(QgsUnitTypes.RenderPoints)


def append_Decorations(symbol, decorations: LineDecoration, context: Context):
    """
    Appends decorations to the given symbol
    """
    if len(decorations.decorations) > 1:
        raise NotImplementedException('Multiple line decorations are not yet supported')
    elif not decorations.decorations:
        return

    decoration = decorations.decorations[0]
    positions = decoration.marker_positions[:]

    marker = Symbol_to_QgsSymbol(decoration.marker, context.symbol_name, context.picture_folder, context.embed_pictures)
    if decoration.flip_all:
        marker.setAngle(270)
    else:
        marker.setAngle(90)

    if 0 in positions:
        # start marker
        line = QgsMarkerLineSymbolLayer(not decoration.fixed_angle)
        start_marker = marker.clone()
        if decoration.flip_first:
            start_marker.setAngle(270)
        line.setSubSymbol(start_marker)
        # TODO - maybe need to offset this by marker width / 4? seems a better match to ESRI
        line.setPlacement(QgsMarkerLineSymbolLayer.FirstVertex)
        symbol.appendSymbolLayer(line)

    if 1 in positions:
        # end marker
        line = QgsMarkerLineSymbolLayer(not decoration.fixed_angle)
        line.setSubSymbol(marker.clone())
        line.setPlacement(QgsMarkerLineSymbolLayer.LastVertex)
        # TODO - maybe need to offset this by marker width / 4? seems a better match to ESRI
        symbol.appendSymbolLayer(line)

    # TODO other positions
    other_positions = [p for p in positions if p not in (0, 1)]
    if other_positions:
        # Would need to use data defined marker placement distance, e.g. $length/3
        # and offset first marker by $length/3 to avoid placing a marker at the start
        # of the line
        raise NotImplementedException('Non start/end decoration positions are not implemented')


def append_CartographicLineSymbolLayer(symbol, layer: CartographicLineSymbolLayer, context: Context):
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

    out.setOffset(layer.offset)
    out.setOffsetUnit(QgsUnitTypes.RenderPoints)

    symbol.appendSymbolLayer(out)

    if layer.decoration is not None:
        append_Decorations(symbol, layer.decoration, context)


def append_MarkerLineSymbolLayer(symbol, layer: MarkerLineSymbolLayer, context: Context):
    """
    Appends a MarkerLineSymbolLayer to a symbol
    """
    template = layer.template

    # first work out total length of pattern
    current_length = 0
    for t in template.pattern_parts:
        current_length += t[0]
        current_length += t[1]

    total_length = current_length * template.pattern_interval

    marker = Symbol_to_QgsSymbol(layer.pattern_marker, context.symbol_name, context.picture_folder,
                                 context.embed_pictures)
    marker.setAngle(90)

    current_offset_from_start = 0
    for t in template.pattern_parts:
        if t[0]:
            # marker
            line = QgsMarkerLineSymbolLayer(True)
            start_marker = marker.clone()
            line.setSubSymbol(start_marker)
            line.setOffset(layer.offset)
            line.setOffsetUnit(QgsUnitTypes.RenderPoints)
            line.setInterval(total_length)
            line.setIntervalUnit(QgsUnitTypes.RenderPoints)
            line.setOffsetAlongLine(current_offset_from_start + template.pattern_interval / 2)
            line.setOffsetAlongLineUnit(QgsUnitTypes.RenderPoints)
            symbol.appendSymbolLayer(line)

            current_offset_from_start += template.pattern_interval * t[0]

        if t[1]:
            # space
            current_offset_from_start += template.pattern_interval * t[1]

    if layer.decoration is not None:
        append_Decorations(symbol, layer.decoration, context)


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


def append_SimpleMarkerSymbolLayer(symbol, layer: SimpleMarkerSymbolLayer,
                                   context: Context):  # pylint: disable=unused-argument
    """
    Appends a SimpleMarkerSymbolLayer to a symbol
    """
    marker_type = marker_type_to_qgis_type(layer.type)
    out = QgsSimpleMarkerSymbolLayer(marker_type, layer.size)
    out.setSizeUnit(QgsUnitTypes.RenderPoints)

    color = symbol_color_to_qcolor(layer.color)

    stroke_only_symbol = layer.type not in ('circle', 'square', 'diamond')
    if not stroke_only_symbol:
        out.setColor(color)
    else:
        out.setStrokeColor(color)

    out.setEnabled(layer.enabled)
    out.setLocked(layer.locked)
    # TODO ArcGIS does not have the same offset/rotation linkages as QGIS does!
    out.setOffset(QPointF(layer.x_offset, layer.y_offset))
    out.setOffsetUnit(QgsUnitTypes.RenderPoints)

    if layer.outline_enabled:
        outline_color = symbol_color_to_qcolor(layer.outline_color)
        if not stroke_only_symbol:
            out.setStrokeColor(outline_color)
            # Better match to how ESRI renders this if we divide the outline width by 2,
            # because ESRI renders the stroke below the symbol. Maybe we should split this
            # into two layers?
            out.setStrokeWidth(layer.outline_width / 2)
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
    elif not stroke_only_symbol:
        out.setStrokeStyle(Qt.NoPen)

    symbol.appendSymbolLayer(out)


def append_ArrowMarkerSymbolLayer(symbol, layer: ArrowMarkerSymbolLayer,
                                  context: Context):  # pylint: disable=unused-argument
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

    # TODO ArcGIS does not have the same offset/rotation linkages as QGIS does!

    out.setOffset(QPointF(layer.x_offset, layer.y_offset))
    out.setOffsetUnit(QgsUnitTypes.RenderPoints)

    angle = 90 - layer.angle
    if angle <= -180:
        angle += 360
    if angle > 180:
        angle -= 360
    out.setAngle(angle)

    out.setEnabled(layer.enabled)
    out.setLocked(layer.locked)

    symbol.appendSymbolLayer(out)


def append_CharacterMarkerSymbolLayer(symbol, layer, context: Context):  # pylint: disable=unused-argument
    """
    Appends a CharacterMarkerSymbolLayer to a symbol
    """
    font_family = layer.font
    character = chr(layer.unicode)
    color = symbol_color_to_qcolor(layer.color)
    angle = convert_angle(layer.angle)

    out = QgsFontMarkerSymbolLayer(font_family, character, layer.size, color, angle)
    out.setSizeUnit(QgsUnitTypes.RenderPoints)

    out.setEnabled(layer.enabled)
    out.setLocked(layer.locked)
    # TODO ArcGIS does not have the same offset/rotation linkages as QGIS does!
    out.setOffset(QPointF(layer.x_offset, layer.y_offset))
    out.setOffsetUnit(QgsUnitTypes.RenderPoints)

    symbol.appendSymbolLayer(out)


def append_PictureMarkerSymbolLayer(symbol, layer: PictureMarkerSymbolLayer, context: Context):
    """
    Appends a PictureMarkerSymbolLayer to a symbol
    """
    picture = layer.picture
    if issubclass(picture.__class__, StdPicture):
        picture = picture.picture

    if issubclass(picture.__class__, EmfPicture):
        path = os.path.join(context.picture_folder, context.symbol_name + '.emf')
        with open(path, 'wb') as f:
            f.write(picture.content)

        svg_path = os.path.join(context.picture_folder, context.symbol_name + '.svg')
        emf_to_svg(path, svg_path)
    else:
        if context.embed_pictures:
            svg = PictureUtils.to_embedded_svg(layer.picture.content)
            svg_base64 = base64.b64encode(svg.encode('UTF-8')).decode('UTF-8')
            svg_path = 'base64:{}'.format(svg_base64)
        else:
            svg = PictureUtils.to_embedded_svg(layer.picture.content)
            svg_path = write_svg(svg, context.symbol_name, context.picture_folder)

    out = QgsSvgMarkerSymbolLayer(svg_path, layer.size, layer.angle)

    out.setEnabled(layer.enabled)
    out.setLocked(layer.locked)
    # TODO ArcGIS does not have the same offset/rotation linkages as QGIS does!
    out.setOffset(QPointF(layer.x_offset, layer.y_offset))
    out.setOffsetUnit(QgsUnitTypes.RenderPoints)

    symbol.appendSymbolLayer(out)


def append_FillSymbolLayer(symbol, layer, context: Context):
    """
    Appends a FillSymbolLayer to a symbol
    """
    if isinstance(layer, (SimpleFillSymbolLayer, ColorSymbol)):
        append_SimpleFillSymbolLayer(symbol, layer, context)
    elif isinstance(layer, LineFillSymbolLayer):
        append_LineFillSymbolLayer(symbol, layer, context)
    elif isinstance(layer, MarkerFillSymbolLayer):
        append_MarkerFillSymbolLayer(symbol, layer, context)
    elif isinstance(layer, PictureFillSymbolLayer):
        append_PictureFillSymbolLayer(symbol, layer, context)
    else:
        raise NotImplementedException('Converting {} not implemented yet'.format(layer.__class__.__name__))


def append_LineSymbolLayer(symbol, layer, context: Context):
    """
    Appends a LineSymbolLayer to a QgsSymbol
    """
    if isinstance(layer, SimpleLineSymbolLayer):
        append_SimpleLineSymbolLayer(symbol, layer, context)
    elif isinstance(layer, CartographicLineSymbolLayer):
        append_CartographicLineSymbolLayer(symbol, layer, context)
    elif isinstance(layer, MarkerLineSymbolLayer):
        append_MarkerLineSymbolLayer(symbol, layer, context)
    elif isinstance(layer, HashLineSymbolLayer):
        raise NotImplementedException(
            'QGIS does not have a hash line symbol type (considering sponsoring this feature!)')
    else:
        raise NotImplementedException('Converting {} not implemented yet'.format(layer.__class__.__name__))


def append_MarkerSymbolLayer(symbol, layer, context: Context):
    """
    Appends a MarkerSymbolLayer to a QgsSymbol
    """
    if isinstance(layer, SimpleMarkerSymbolLayer):
        append_SimpleMarkerSymbolLayer(symbol, layer, context)
    elif isinstance(layer, ArrowMarkerSymbolLayer):
        append_ArrowMarkerSymbolLayer(symbol, layer, context)
    elif isinstance(layer, CharacterMarkerSymbolLayer):
        append_CharacterMarkerSymbolLayer(symbol, layer, context)
    elif isinstance(layer, PictureMarkerSymbolLayer):
        append_PictureMarkerSymbolLayer(symbol, layer, context)
    else:
        raise NotImplementedException('Converting {} not implemented yet'.format(layer.__class__.__name__))


def append_SymbolLayer_to_QgsSymbolLayer(symbol, layer, context: Context):
    """
    Appends a SymbolLayer to a QgsSymbolLayer
    """
    if issubclass(layer.__class__, SymbolLayer):
        if issubclass(layer.__class__, FillSymbolLayer):
            append_FillSymbolLayer(symbol, layer, context)
        elif issubclass(layer.__class__, LineSymbolLayer):
            append_LineSymbolLayer(symbol, layer, context)
        elif issubclass(layer.__class__, MarkerSymbolLayer):
            append_MarkerSymbolLayer(symbol, layer, context)
        else:
            raise NotImplementedException('Converting {} not implemented yet'.format(layer.__class__.__name__))
    else:
        for l in layer.levels:
            append_SymbolLayer_to_QgsSymbolLayer(symbol, l, context)


def add_symbol_layers(out, symbol, context: Context):
    """
    Adds all symbol layers to a symbol
    """
    out.deleteSymbolLayer(0)
    if issubclass(symbol.__class__, SymbolLayer):
        append_SymbolLayer_to_QgsSymbolLayer(out, symbol, context)
    else:
        for l in symbol.levels:
            append_SymbolLayer_to_QgsSymbolLayer(out, l, context)
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
        """
        Converts saturation/values range from 0-100 in esri symbols, to 0-255 for QGIS
        """
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


def Symbol_to_QgsSymbol(symbol, symbol_name: str, picture_folder: str, embed_pictures: bool):
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

    context = Context()
    context.symbol_name = symbol_name
    context.picture_folder = picture_folder
    context.embed_pictures = embed_pictures
    add_symbol_layers(out, symbol, context)

    return out
