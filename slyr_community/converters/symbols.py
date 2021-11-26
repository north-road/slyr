#!/usr/bin/env python
# pylint: disable=too-many-lines

# /***************************************************************************
# symbols.py
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
Symbol converter
"""

import base64
import math
import os
import subprocess
from typing import Union, Tuple

from qgis.core import (Qgis,
                       QgsUnitTypes,
                       QgsSimpleLineSymbolLayer,
                       QgsSimpleFillSymbolLayer,
                       QgsFillSymbol,
                       QgsLineSymbol,
                       QgsMarkerSymbol,
                       QgsEllipseSymbolLayer,
                       QgsSimpleMarkerSymbolLayer,
                       QgsSvgMarkerSymbolLayer,
                       QgsSVGFillSymbolLayer,
                       QgsSimpleMarkerSymbolLayerBase,
                       QgsFontMarkerSymbolLayer,
                       QgsGradientColorRamp,
                       QgsMarkerLineSymbolLayer,
                       QgsLinePatternFillSymbolLayer,
                       QgsPointPatternFillSymbolLayer,
                       QgsRasterFillSymbolLayer,
                       QgsGradientFillSymbolLayer,
                       QgsGradientStop,
                       QgsShapeburstFillSymbolLayer
                       )

try:
    from qgis.core import QgsHashedLineSymbolLayer

    HAS_HASHED_LINE_SYMBOL_LAYER = True
except ImportError:
    HAS_HASHED_LINE_SYMBOL_LAYER = False

try:
    from qgis.core import QgsRasterMarkerSymbolLayer
except ImportError:
    pass

from qgis.PyQt.QtCore import (
    Qt,
    QPointF,
    QLineF,
    QBuffer
)
from qgis.PyQt.QtGui import (
    QColor,
    QFont,
    QFontDatabase,
    QFontMetricsF,
    QPainterPath,
    QPainter,
    QBrush
)
from qgis.PyQt.QtSvg import QSvgGenerator, QSvgRenderer

from slyr_community.parser.objects.multi_layer_symbols import (
    MultiLayerFillSymbol,
    MultiLayerLineSymbol,
    MultiLayerMarkerSymbol
)
from slyr_community.parser.objects.symbol_layer import SymbolLayer
from slyr_community.parser.objects.line_symbol_layer import (
    SimpleLineSymbol,
    CartographicLineSymbol,
    MarkerLineSymbol,
    HashLineSymbol,
    LineSymbolLayer)
from slyr_community.parser.objects.fill_symbol_layer import (
    FillSymbolLayer,
    SimpleFillSymbol,
    ColorSymbol,
    LineFillSymbol,
    MarkerFillSymbol,
    PictureFillSymbol,
    GradientFillSymbol
)
from slyr_community.parser.objects.marker_symbol_layer import (
    MarkerSymbolLayer,
    SimpleMarkerSymbol,
    ArrowMarkerSymbol,
    CharacterMarkerSymbol,
    PictureMarkerSymbol
)
from slyr_community.parser.exceptions import NotImplementedException
from slyr_community.converters.context import Context
from slyr_community.converters.color import ColorConverter
from slyr_community.converters.decorations import DecorationConverter
from slyr_community.parser.objects.simple_line3d_symbol import SimpleLine3DSymbol
from slyr_community.parser.objects.marker3d_symbol import Marker3DSymbol
from slyr_community.parser.objects.simple_marker3d_symbol import SimpleMarker3DSymbol
from slyr_community.parser.objects.character_marker3d_symbol import CharacterMarker3DSymbol
from slyr_community.parser.objects.texture_fill_symbol import TextureFillSymbol
from slyr_community.parser.objects.color_ramp_symbol import ColorRampSymbol
from slyr_community.parser.objects.ramps import ColorRamp
from slyr_community.converters.color_ramp import ColorRampConverter
from slyr_community.converters.utils import ConversionUtils
from slyr_community.converters.pictures import PictureUtils
from slyr_community.parser.objects.picture import (
    EmfPicture,
    StdPicture,
    BmpPicture
)
from slyr_community.bintools.file_utils import FileUtils


class SymbolConverter:  # pylint: disable=too-many-public-methods
    """
    Converts ArcObjects symbols to QGIS symbols
    """

    @staticmethod
    def Symbol_to_QgsSymbol(symbol, context: Context):
        """
        Converts a raw Symbol to a QgsSymbol
        """
        if issubclass(symbol.__class__, (MultiLayerFillSymbol, FillSymbolLayer, TextureFillSymbol)):
            out = QgsFillSymbol()
        elif issubclass(symbol.__class__, (MultiLayerLineSymbol, LineSymbolLayer, SimpleLine3DSymbol)):
            out = QgsLineSymbol()
        elif issubclass(symbol.__class__, (
                MultiLayerMarkerSymbol, MarkerSymbolLayer, Marker3DSymbol, SimpleMarker3DSymbol,
                CharacterMarker3DSymbol)):
            if isinstance(symbol, MultiLayerMarkerSymbol) and symbol.halo and context.unsupported_object_callback:
                context.unsupported_object_callback(
                    '{}: Marker halos are not supported by QGIS'.format(context.layer_name or context.symbol_name),
                    level=Context.WARNING)
            out = QgsMarkerSymbol()
        elif issubclass(symbol.__class__, ColorRamp):
            out = ColorRampConverter.ColorRamp_to_QgsColorRamp(symbol)
            return out
        elif issubclass(symbol.__class__, ColorRampSymbol):
            out = QgsFillSymbol()
            SymbolConverter.append_GradientFillSymbolLayer(out, symbol, context)
            out.deleteSymbolLayer(0)
            return out
        else:
            raise NotImplementedException(
                '{} symbols require the licensed version of SLYR'.format(symbol.__class__.__name__))

        SymbolConverter.add_symbol_layers(out, symbol, context)

        return out

    @staticmethod
    def symbol_to_color(symbol, context: Context):
        """
        Converts an ESRI symbol to a single color best representing the symbol
        """
        s = SymbolConverter.Symbol_to_QgsSymbol(symbol, context)
        if issubclass(symbol.__class__, MultiLayerFillSymbol):
            all_null = True
            for layer in symbol.layers:
                if isinstance(layer, SimpleFillSymbol) and symbol.layers[0].fill_style == SimpleFillSymbol.STYLE_NULL:
                    continue
                all_null = False
            if all_null:
                c = s.color()
                c.setAlpha(0)
                return c
            else:
                return s.color()
        elif isinstance(symbol, SimpleFillSymbol):
            if symbol.fill_style == SimpleFillSymbol.STYLE_NULL:
                c = s.color()
                c.setAlpha(0)
                return c
            return s.color()

        return s.color()

    @staticmethod
    def symbol_to_line_width(symbol, context: Context) -> float:
        """
        Converts an ESRI symbol to a single line width value best representing the symbol
        """
        s = SymbolConverter.Symbol_to_QgsSymbol(symbol, context)
        return s.width()

    @staticmethod
    def symbol_to_marker_size(symbol, context: Context) -> float:
        """
        Converts an ESRI symbol to a single marker size value best representing the symbol
        """
        s = SymbolConverter.Symbol_to_QgsSymbol(symbol, context)
        return s.size()

    @staticmethod
    def symbol_to_marker_shape(symbol, context: Context) -> str:  # pylint: disable=unused-argument
        """
        Converts an ESRI symbol to a marker shape string ("circle" or "square") best representing the symbol
        """
        if isinstance(symbol, SimpleMarkerSymbol):
            return symbol.type

        elif isinstance(symbol, MultiLayerMarkerSymbol) and len(symbol.layers) == 1 and isinstance(symbol.layers[0],
                                                                                                   SimpleMarkerSymbol):
            return symbol.layers[0].type

        return 'circle'

    @staticmethod
    def add_symbol_layers(out, symbol, context: Context):
        """
        Adds all symbol layers to a symbol
        """
        out.deleteSymbolLayer(0)
        if issubclass(symbol.__class__, SymbolLayer):
            SymbolConverter.append_SymbolLayer_to_QgsSymbolLayer(out, symbol, context)
        else:
            for layer in symbol.layers:
                SymbolConverter.append_SymbolLayer_to_QgsSymbolLayer(out, layer, context)
            if symbol.symbol_level != 0xffffffff:
                # 0xffffffff = sub layers have own level
                for i in range(out.symbolLayerCount()):
                    out.symbolLayer(i).setRenderingPass(symbol.symbol_level)

        if out.symbolLayerCount() == 0:
            # we appended nothing! Add a dummy invisible layer to avoid QGIS adding a default layer to this
            if isinstance(out, QgsMarkerSymbol):
                layer = QgsSimpleMarkerSymbolLayer(color=QColor(0, 0, 0, 0))
                layer.setStrokeStyle(Qt.NoPen)
                out.appendSymbolLayer(layer)
            elif isinstance(out, QgsLineSymbol):
                layer = QgsSimpleLineSymbolLayer(color=QColor(0, 0, 0, 0), penStyle=Qt.NoPen)
                out.appendSymbolLayer(layer)
            elif isinstance(out, QgsFillSymbol):
                layer = QgsSimpleFillSymbolLayer(color=QColor(0, 0, 0, 0), style=Qt.NoBrush, strokeStyle=Qt.NoPen)
                out.appendSymbolLayer(layer)

        return out

    @staticmethod
    def append_SymbolLayer_to_QgsSymbolLayer(symbol,  # pylint: disable=too-many-statements,too-many-branches
                                             layer,
                                             context: Context):
        """
        Appends a SymbolLayer to a QgsSymbolLayer
        """
        if issubclass(layer.__class__, SymbolLayer):
            if issubclass(layer.__class__, FillSymbolLayer):
                SymbolConverter.append_FillSymbolLayer(symbol, layer, context)
            elif issubclass(layer.__class__, LineSymbolLayer):
                SymbolConverter.append_LineSymbolLayer(symbol, layer, context)
            elif issubclass(layer.__class__, MarkerSymbolLayer):
                SymbolConverter.append_MarkerSymbolLayer(symbol, layer, context)
            elif issubclass(layer.__class__, Marker3DSymbol):
                SymbolConverter.append_Marker3DSymbolLayer(symbol, layer, context)
            elif issubclass(layer.__class__, SimpleMarker3DSymbol):
                SymbolConverter.append_SimpleMarker3DSymbolLayer(symbol, layer, context)
            elif issubclass(layer.__class__, SimpleLine3DSymbol):
                SymbolConverter.append_SimpleLine3DSymbolLayer(symbol, layer, context)
            elif issubclass(layer.__class__, CharacterMarker3DSymbol):
                SymbolConverter.append_CharacterMarker3DSymbolLayer(symbol, layer, context)
            elif issubclass(layer.__class__, TextureFillSymbol):
                SymbolConverter.append_TextureFillSymbolLayer(symbol, layer, context)
            elif issubclass(layer.__class__, ColorRampSymbol):
                SymbolConverter.append_FillSymbolLayer(symbol, layer, context)
            else:
                raise NotImplementedException('Converting {} not implemented yet'.format(layer.__class__.__name__))
        else:
            for sublayer in layer.layers:
                SymbolConverter.append_SymbolLayer_to_QgsSymbolLayer(symbol, sublayer, context)

    @staticmethod
    def append_FillSymbolLayer(symbol, layer, context: Context):
        """
        Appends a FillSymbolLayer to a symbol
        """
        if isinstance(layer, (SimpleFillSymbol, ColorSymbol)):
            SymbolConverter.append_SimpleFillSymbolLayer(symbol, layer, context)
        elif isinstance(layer, LineFillSymbol):
            SymbolConverter.append_LineFillSymbolLayer(symbol, layer, context)
        elif isinstance(layer, MarkerFillSymbol):
            SymbolConverter.append_MarkerFillSymbolLayer(symbol, layer, context)
        elif isinstance(layer, PictureFillSymbol):
            SymbolConverter.append_PictureFillSymbolLayer(symbol, layer, context)
        elif isinstance(layer, GradientFillSymbol):
            SymbolConverter.append_GradientFillSymbolLayer(symbol, layer, context)
        else:
            raise NotImplementedException('Converting {} not implemented yet'.format(layer.__class__.__name__))

    @staticmethod
    def append_LineSymbolLayer(symbol, layer, context: Context):
        """
        Appends a LineSymbolLayer to a QgsSymbol
        """
        if isinstance(layer, SimpleLineSymbol):
            SymbolConverter.append_SimpleLineSymbolLayer(symbol, layer, context)
        elif isinstance(layer, CartographicLineSymbol):
            SymbolConverter.append_CartographicLineSymbolLayer(symbol, layer, context)
        elif isinstance(layer, (MarkerLineSymbol, HashLineSymbol)):
            SymbolConverter.append_TemplatedLineSymbolLayer(symbol, layer, context)
        else:
            raise NotImplementedException('Converting {} not implemented yet'.format(layer.__class__.__name__))

    @staticmethod
    def append_MarkerSymbolLayer(symbol, layer, context: Context):
        """
        Appends a MarkerSymbolLayer to a QgsSymbol
        """
        if isinstance(layer, SimpleMarkerSymbol):
            SymbolConverter.append_SimpleMarkerSymbolLayer(symbol, layer, context)
        elif isinstance(layer, ArrowMarkerSymbol):
            SymbolConverter.append_ArrowMarkerSymbolLayer(symbol, layer, context)
        elif isinstance(layer, CharacterMarkerSymbol):
            SymbolConverter.append_CharacterMarkerSymbolLayer(symbol, layer, context)
        elif isinstance(layer, PictureMarkerSymbol):
            SymbolConverter.append_PictureMarkerSymbolLayer(symbol, layer, context)
        else:
            raise NotImplementedException('Converting {} not implemented yet'.format(layer.__class__.__name__))

    @staticmethod
    def append_SimpleFillSymbolLayer(symbol,  # pylint: disable=too-many-branches,too-many-statements
                                     layer: SimpleFillSymbol,
                                     context: Context):
        """
        Appends a SimpleFillSymbolLayer to a symbol
        """
        fill_color = ColorConverter.color_to_qcolor(layer.color)
        out = QgsSimpleFillSymbolLayer(fill_color)
        out.setEnabled(layer.enabled)
        out.setLocked(layer.locked)
        if layer.symbol_level != 0xffffffff:
            out.setRenderingPass(layer.symbol_level)

        if isinstance(layer, SimpleFillSymbol):
            if layer.outline and not isinstance(layer.outline, MultiLayerLineSymbol):
                # these properties are not supported in QGIS simple fill, so we need
                # to add an additional outline layer to support them
                uses_complex_outline = (hasattr(layer.outline, 'offset') and layer.outline.offset) \
                                       or (hasattr(layer.outline, 'template') and
                                           layer.outline.template and
                                           len(layer.outline.template.pattern_parts) > 0) \
                                       or (hasattr(layer.outline, 'decoration') and
                                           layer.outline.decoration)
                if not uses_complex_outline:
                    # great, we can avoid the extra symbol layer!
                    if isinstance(layer.outline, (SimpleLineSymbol, CartographicLineSymbol)):
                        out.setStrokeColor(ColorConverter.color_to_qcolor(layer.outline.color))
                        out.setStrokeWidth(context.convert_size(context.fix_line_width(layer.outline.width)))
                        out.setStrokeWidthUnit(context.units)
                    if isinstance(layer.outline, SimpleLineSymbol):
                        out.setStrokeStyle(
                            ConversionUtils.symbol_pen_to_qpenstyle(
                                layer.outline.line_type) if layer.outline.width > 0 else Qt.NoPen)
                    if isinstance(layer.outline, CartographicLineSymbol):
                        out.setPenJoinStyle(ConversionUtils.symbol_pen_to_qpenjoinstyle(layer.outline.join))
                        if layer.outline.width <= 0:
                            out.setStrokeStyle(Qt.NoPen)
                    # better matching of null stroke color to QGIS symbology
                    if out.strokeColor().alpha() == 0:
                        out.setStrokeStyle(Qt.NoPen)

                    if context.apply_conversion_tweaks and \
                            (out.strokeColor().alpha() == 0 or out.strokeStyle() == Qt.NoPen) and \
                            (out.color().alpha() == 0):
                        # skip empty layers
                        return

                    symbol.appendSymbolLayer(out)
                else:
                    out.setStrokeStyle(Qt.NoPen)

                    if not context.apply_conversion_tweaks or out.color().alpha() != 0:
                        symbol.appendSymbolLayer(out)

                    SymbolConverter.append_SymbolLayer_to_QgsSymbolLayer(symbol, layer.outline, context)
            elif isinstance(layer.outline, MultiLayerLineSymbol):
                # outline is a symbol itself
                out.setStrokeStyle(Qt.NoPen)

                if not context.apply_conversion_tweaks or out.color().alpha() != 0:
                    symbol.appendSymbolLayer(out)

                # get all layers from outline
                SymbolConverter.append_SymbolLayer_to_QgsSymbolLayer(symbol, layer.outline, context)
            else:
                out.setStrokeStyle(Qt.NoPen)

                if not context.apply_conversion_tweaks or out.color().alpha() != 0:
                    symbol.appendSymbolLayer(out)

            if layer.fill_style == SimpleFillSymbol.STYLE_NULL:
                out.setBrushStyle(Qt.NoBrush)
            elif layer.fill_style == SimpleFillSymbol.STYLE_HORIZONTAL:
                out.setBrushStyle(Qt.HorPattern)
            elif layer.fill_style == SimpleFillSymbol.STYLE_VERTICAL:
                out.setBrushStyle(Qt.VerPattern)
            elif layer.fill_style == SimpleFillSymbol.STYLE_FORWARD_DIAGONAL:
                out.setBrushStyle(Qt.FDiagPattern)
            elif layer.fill_style == SimpleFillSymbol.STYLE_BACKWARD_DIAGONAL:
                out.setBrushStyle(Qt.BDiagPattern)
            elif layer.fill_style == SimpleFillSymbol.STYLE_CROSS:
                out.setBrushStyle(Qt.CrossPattern)
            elif layer.fill_style == SimpleFillSymbol.STYLE_DIAGONAL_CROSS:
                out.setBrushStyle(Qt.DiagCrossPattern)

        elif isinstance(layer, ColorSymbol):
            out.setStrokeStyle(Qt.NoPen)

            if not context.apply_conversion_tweaks or out.color().alpha() != 0:
                symbol.appendSymbolLayer(out)

    @staticmethod
    def append_LineFillSymbolLayer(symbol, layer: LineFillSymbol, context: Context):
        """
        Appends a LineFillSymbolLayer to a symbol
        """
        line = SymbolConverter.Symbol_to_QgsSymbol(layer.line, context)

        out = QgsLinePatternFillSymbolLayer()
        out.setEnabled(layer.enabled)
        out.setLocked(layer.locked)
        if layer.symbol_level != 0xffffffff:
            out.setRenderingPass(layer.symbol_level)
        out.setSubSymbol(line)
        out.setLineAngle(layer.angle)

        separation = layer.separation
        # if context.apply_conversion_tweaks:
        #    min_separation = 5 * max(line.width(),
        #                             0.5 if line.symbolLayer(0).widthUnit() == QgsUnitTypes.RenderPoints else 0.18)
        #    separation = max(min_separation, separation)
        #    if context.units == QgsUnitTypes.RenderMillimeters:
        #        separation *= 0.352

        out.setDistance(context.convert_size(separation))
        out.setDistanceUnit(context.units)
        out.setOffset(context.convert_size(layer.offset))
        out.setOffsetUnit(context.units)

        symbol.appendSymbolLayer(out)
        if isinstance(layer.outline, MultiLayerLineSymbol):
            # get all layers from outline
            SymbolConverter.append_SymbolLayer_to_QgsSymbolLayer(symbol, layer.outline, context)
        elif layer.outline:
            SymbolConverter.append_SymbolLayer_to_QgsSymbolLayer(symbol, layer.outline, context)

    @staticmethod
    def append_GradientFillSymbolLayer(symbol,  # pylint: disable=too-many-statements,too-many-branches
                                       layer: Union[GradientFillSymbol, ColorRampSymbol],
                                       context: Context):
        """
        Appends a append_GradientFillSymbolLayer to a symbol
        """
        if isinstance(layer, ColorRampSymbol):
            ramp = ColorRampConverter.ColorRamp_to_QgsColorRamp(layer.color_ramp)
        else:
            ramp = ColorRampConverter.ColorRamp_to_QgsColorRamp(layer.ramp)

        def scale_ramp(ramp, percent):
            # percent has a different meaning here -- it effectively stretches the ramp
            if percent < 1:
                # only support this for gradient ramps
                if isinstance(ramp, QgsGradientColorRamp):
                    stops = ramp.stops()
                    for s in stops:
                        s.offset = 1 - percent * (1 - s.offset)
                    # also need to insert a new first color stop
                    stops = [QgsGradientStop(1 - percent, ramp.color1())] + stops
                    ramp.setStops(stops)

        if isinstance(layer, GradientFillSymbol) \
                and layer.type in (GradientFillSymbol.RECTANGULAR, GradientFillSymbol.BUFFERED):
            if context.unsupported_object_callback and layer.type == GradientFillSymbol.RECTANGULAR:
                context.unsupported_object_callback(
                    '{}: Rectangular gradients are not supported in QGIS, using buffered gradient instead'.format(
                        context.layer_name or context.symbol_name),
                    level=Context.WARNING)

            if Qgis.QGIS_VERSION_INT < 30900:
                # can cause crash in < 3.10
                if context.unsupported_object_callback:
                    context.unsupported_object_callback(
                        '{}: Buffered gradients are not supported in QGIS < 3.10'.format(
                            context.layer_name or context.symbol_name),
                        Context.WARNING)
                    return
                else:
                    raise NotImplementedException('Buffered gradients are not supported in QGIS < 3.10')
            out = QgsShapeburstFillSymbolLayer()
            out.setColorType(QgsShapeburstFillSymbolLayer.ColorRamp)
            ramp.invert()
            scale_ramp(ramp, layer.percent)
            ramp.invert()
            out.setColorRamp(ramp)
            out.setEnabled(layer.enabled)
            out.setLocked(layer.locked)
            if layer.symbol_level != 0xffffffff:
                out.setRenderingPass(layer.symbol_level)
            symbol.appendSymbolLayer(out)
            return
        elif isinstance(layer, GradientFillSymbol) and layer.type == GradientFillSymbol.CIRCULAR:
            ref_1 = QPointF(0.5, 0.5)
            ref_2 = QPointF(1.0, 0.5)
            gradient_type = QgsGradientFillSymbolLayer.Radial
            # yep!!
            ramp.invert()
            scale_ramp(ramp, layer.percent)
        elif isinstance(layer, ColorRampSymbol) or layer.type == GradientFillSymbol.LINEAR:
            l1 = QLineF(0.5, 0.5, 1, 0.5)
            l2 = QLineF(0.5, 0.5, 0, 0.5)

            if isinstance(layer, ColorRampSymbol):
                angle = 0 if layer.horizontal else 270
                percent = 100
            else:
                percent = layer.percent
                angle = layer.angle

            # angle of
            # 0: right to left
            # 90: top to bottom
            # 180: left to right
            # 270: bottom to top
            l1.setAngle(angle)
            l2.setAngle(angle + 180)

            ref_1 = l1.p2()
            ref_2 = l2.p2()

            if percent < 100:
                l1 = QLineF(ref_1, ref_2)
                l1.setLength(l1.length() * percent)
                ref_2 = l1.p2()

            gradient_type = QgsGradientFillSymbolLayer.Linear

        out = QgsGradientFillSymbolLayer(gradientColorType=QgsGradientFillSymbolLayer.ColorRamp,
                                         gradientType=gradient_type)
        out.setColorRamp(ramp)
        out.setReferencePoint1(ref_1)
        out.setReferencePoint2(ref_2)
        if isinstance(layer, GradientFillSymbol):
            out.setEnabled(layer.enabled)
            out.setLocked(layer.locked)
            if layer.symbol_level != 0xffffffff:
                out.setRenderingPass(layer.symbol_level)
        symbol.appendSymbolLayer(out)

    @staticmethod
    def append_MarkerFillSymbolLayer(symbol, layer: MarkerFillSymbol, context: Context):
        """
        Appends a MarkerFillSymbolLayer to a symbol
        """
        if layer.random and Qgis.QGIS_VERSION_INT < 31100 and context.unsupported_object_callback:
            context.unsupported_object_callback(
                '{}: Random marker fills are only supported on QGIS 3.12 or later'.format(
                    context.layer_name or context.symbol_name),
                level=Context.WARNING)

        if Qgis.QGIS_VERSION_INT < 30700 and context.unsupported_object_callback:
            if layer.offset_x or layer.offset_y:
                context.unsupported_object_callback(
                    '{}: Marker fill offset X or Y is only supported on QGIS 3.8 or later'.format(
                        context.layer_name or context.symbol_name), level=Context.WARNING)

        marker = SymbolConverter.Symbol_to_QgsSymbol(layer.marker, context)

        if layer.random and Qgis.QGIS_VERSION_INT >= 31100:
            from qgis.core import QgsRandomMarkerFillSymbolLayer  # pylint: disable=import-outside-toplevel

            density = layer.separation_x * layer.separation_y / 10
            out = QgsRandomMarkerFillSymbolLayer(1, QgsRandomMarkerFillSymbolLayer.DensityBasedCount, density)
            out.setClipPoints(True)
        else:
            out = QgsPointPatternFillSymbolLayer()
            out.setDistanceX(context.convert_size(layer.separation_x))
            out.setDistanceXUnit(context.units)
            out.setDistanceY(context.convert_size(layer.separation_y))
            out.setDistanceYUnit(context.units)

            # Offset only supported since QGIS 3.8
            if hasattr(out, 'setOffsetX'):
                out.setOffsetX(layer.offset_x)
                out.setOffsetXUnit(QgsUnitTypes.RenderPoints)
                out.setOffsetY(layer.offset_y)
                out.setOffsetYUnit(QgsUnitTypes.RenderPoints)

        out.setSubSymbol(marker)
        out.setEnabled(layer.enabled)
        out.setLocked(layer.locked)
        if layer.symbol_level != 0xffffffff:
            out.setRenderingPass(layer.symbol_level)

        symbol.appendSymbolLayer(out)
        if isinstance(layer.outline, MultiLayerLineSymbol):
            # get all layers from outline
            SymbolConverter.append_SymbolLayer_to_QgsSymbolLayer(symbol, layer.outline, context)
        elif layer.outline:
            SymbolConverter.append_SymbolLayer_to_QgsSymbolLayer(symbol, layer.outline, context)

    @staticmethod
    def symbol_name_to_filename(symbol_name: str, picture_folder: str, extension: str) -> str:
        """
        Returns a new unique filename for the given symbol to use
        """
        safe_symbol_name = FileUtils.clean_symbol_name_for_file(symbol_name)
        path = os.path.join(picture_folder, safe_symbol_name + '.' + extension)
        counter = 1
        while os.path.exists(path):
            path = os.path.join(picture_folder, safe_symbol_name + '_' + str(counter) + '.' + extension)
            counter += 1

        return path

    @staticmethod
    def emf_to_svg(emf_path: str, svg_path: str, inkscape_path: str = None, context: Context = None):
        """
        Converts an EMF file to an SVG file (using inkscape)
        """
        binary = 'inkscape'
        if inkscape_path is not None:
            binary = inkscape_path

        export_args = [binary,
                       '--file',
                       emf_path,
                       '--export-plain-svg',
                       svg_path]

        # print(' '.join(export_args))

        CREATE_NO_WINDOW = 0x08000000
        try:
            try:
                _ = subprocess.run(export_args, stdout=subprocess.PIPE,  # pylint: disable=subprocess-run-check
                                   creationflags=CREATE_NO_WINDOW)
            except ValueError:
                _ = subprocess.run(export_args, stdout=subprocess.PIPE)  # pylint: disable=subprocess-run-check
        except FileNotFoundError:
            pass

        if not os.path.exists(svg_path):
            # bah, inkscape changed parameters!
            export_args = [binary,
                           '--export-plain-svg',
                           '--export-file',
                           svg_path,
                           emf_path
                           ]

            # print(' '.join(export_args))

            CREATE_NO_WINDOW = 0x08000000
            try:
                try:
                    _ = subprocess.run(export_args, stdout=subprocess.PIPE,  # pylint: disable=subprocess-run-check
                                       creationflags=CREATE_NO_WINDOW)
                except ValueError:
                    _ = subprocess.run(export_args, stdout=subprocess.PIPE)  # pylint: disable=subprocess-run-check
            except FileNotFoundError:
                pass

        if not os.path.exists(svg_path):
            # bah, inkscape changed parameters YET AGAIN!!!
            export_args = [binary,
                           '--export-plain-svg',
                           '-o',
                           svg_path,
                           emf_path
                           ]

            # print(' '.join(export_args))

            CREATE_NO_WINDOW = 0x08000000
            try:
                try:
                    _ = subprocess.run(export_args, stdout=subprocess.PIPE,  # pylint: disable=subprocess-run-check
                                       creationflags=CREATE_NO_WINDOW)
                except ValueError:
                    _ = subprocess.run(export_args, stdout=subprocess.PIPE)  # pylint: disable=subprocess-run-check
            except FileNotFoundError:
                pass

        if not os.path.exists(svg_path):
            # didn't work
            if context.unsupported_object_callback:
                context.unsupported_object_callback(
                    'Conversion of EMF content requires a valid path to an Inkscape install setup in the SLYR options',
                    level=Context.CRITICAL)

    @staticmethod
    def write_svg(content: str, symbol_name: str, picture_folder: str):
        """
        Writes a picture binary content to an SVG file
        """
        path = SymbolConverter.symbol_name_to_filename(symbol_name, picture_folder, 'svg')
        with open(path, 'wt', encoding='utf8') as f:
            f.write(content)
        return path

    @staticmethod
    def get_picture_data(picture, fg, bg, trans, context=None):
        """
        Retrieves picture binary content, converting raster colors if necessary
        """
        if issubclass(picture.__class__, StdPicture):
            picture = picture.picture
        fg_color = ColorConverter.color_to_qcolor(fg) if fg else None
        bg_color = ColorConverter.color_to_qcolor(bg) if bg else None
        trans_color = ColorConverter.color_to_qcolor(trans) if trans and not trans.is_null else None
        if picture is None or picture.content is None:
            if context and context.unsupported_object_callback:
                context.unsupported_object_callback(
                    '{}: Picture data is missing or corrupt'.format(context.layer_name or context.symbol_name),
                    level=Context.CRITICAL)
            return None
        else:
            return PictureUtils.set_colors(picture.content, fg_color, bg_color, trans_color)

    @staticmethod
    def write_picture(picture, symbol_name: str, picture_folder: str, fg, bg, trans, context=None):
        """
        Writes a picture binary content to a file, converting raster colors if necessary
        """
        new_content = SymbolConverter.get_picture_data(picture, fg, bg, trans, context=context)

        path = SymbolConverter.symbol_name_to_filename(symbol_name, picture_folder, 'png')
        PictureUtils.to_png(new_content, path)
        return path

    @staticmethod
    def append_PictureFillSymbolLayer(symbol,  # pylint: disable=too-many-statements,too-many-branches,too-many-locals
                                      layer: PictureFillSymbol,
                                      context: Context):
        """
        Appends a PictureFillSymbolLayer to a symbol
        """
        if Qgis.QGIS_VERSION_INT < 30700 and context.unsupported_object_callback:
            if layer.offset_x or layer.offset_y:
                context.unsupported_object_callback(
                    '{}: Marker fill offset X or Y is only supported on QGIS 3.8 or later'.format(
                        context.layer_name or context.symbol_name), level=Context.WARNING)
        if (layer.separation_x or layer.separation_y) and context.unsupported_object_callback:
            context.unsupported_object_callback('{}: Picture fill separation X or Y is not supported by QGIS'.format(
                context.layer_name or context.symbol_name), level=Context.WARNING)

        picture = layer.picture
        if issubclass(picture.__class__, StdPicture):
            picture = picture.picture

        if issubclass(picture.__class__, EmfPicture):
            path = SymbolConverter.symbol_name_to_filename(context.symbol_name, context.get_picture_store_folder(),
                                                           'emf')
            with open(path, 'wb') as f:
                f.write(picture.content)

            svg_path = SymbolConverter.symbol_name_to_filename(context.symbol_name, context.get_picture_store_folder(),
                                                               'svg')
            SymbolConverter.emf_to_svg(path, svg_path, inkscape_path=context.inkscape_path, context=context)
            if not os.path.exists(svg_path):
                if context.unsupported_object_callback:
                    context.unsupported_object_callback(
                        '{}: Conversion of EMF picture failed'.format(context.layer_name or context.symbol_name),
                        level=Context.CRITICAL)

            width_in_in_points = layer.scale_x * QSvgRenderer(svg_path).viewBoxF().width()

            if context.embed_pictures and os.path.exists(svg_path):
                with open(svg_path, 'rb') as svg_file:
                    svg_content = base64.b64encode(svg_file.read()).decode('UTF-8')
                svg_path = 'base64:{}'.format(svg_content)
            else:
                svg_path = context.convert_path(svg_path)

            out = QgsSVGFillSymbolLayer(svg_path, context.convert_size(width_in_in_points),
                                        ConversionUtils.convert_angle(layer.angle))
            out.setPatternWidthUnit(context.units)
            outline = QgsLineSymbol()
            outline.changeSymbolLayer(0, QgsSimpleLineSymbolLayer(penStyle=Qt.NoPen))
            out.setSubSymbol(outline)
        else:
            # use raster fill
            if context.embed_pictures and Qgis.QGIS_VERSION_INT >= 30600:
                picture_data = SymbolConverter.get_picture_data(picture, layer.color_foreground, layer.color_background,
                                                                None, context=context)
                if picture_data:
                    image_base64 = base64.b64encode(picture_data).decode('UTF-8')
                    image_path = 'base64:{}'.format(image_base64)
                else:
                    image_path = ''
            else:
                image_path = SymbolConverter.write_picture(picture, context.symbol_name,
                                                           context.get_picture_store_folder(),
                                                           layer.color_foreground,
                                                           layer.color_background,
                                                           None, context=context)

            out = QgsRasterFillSymbolLayer(image_path)

            if picture and picture.content:
                # convert to points, so that print layouts work nicely. It's a better match for Arc anyway
                width_in_pixels = layer.scale_x * PictureUtils.width_pixels(picture.content)
                width_in_in_points = width_in_pixels / 96 * 72

                out.setWidth(context.convert_size(width_in_in_points))
                out.setWidthUnit(context.units)

            out.setAngle(ConversionUtils.convert_angle(layer.angle))

        out.setEnabled(layer.enabled)
        out.setLocked(layer.locked)
        if layer.symbol_level != 0xffffffff:
            out.setRenderingPass(layer.symbol_level)
        symbol.appendSymbolLayer(out)
        if isinstance(layer.outline, MultiLayerLineSymbol):
            # get all layers from outline
            SymbolConverter.append_SymbolLayer_to_QgsSymbolLayer(symbol, layer.outline, context)
        elif layer.outline:
            SymbolConverter.append_SymbolLayer_to_QgsSymbolLayer(symbol, layer.outline, context)

    @staticmethod
    def append_TextureFillSymbolLayer(symbol, layer: TextureFillSymbol, context: Context):
        """
        Appends a TextureFillSymbol to a symbol
        """
        if not layer.texture:
            return

        picture = layer.texture.picture
        if not picture:
            return

        if context.unsupported_object_callback:
            if context.layer_name:
                context.unsupported_object_callback(
                    '{}: 3D texture fill was converted to a 2d fill'.format(context.layer_name),
                    level=Context.WARNING)
            elif context.symbol_name:
                context.unsupported_object_callback(
                    '{}: 3D texture fill was converted to a 2d fill'.format(context.symbol_name), level=Context.WARNING)
            else:
                context.unsupported_object_callback('3D texture fill was converted to a 2d fill', level=Context.WARNING)

        # use raster fill
        if context.embed_pictures and Qgis.QGIS_VERSION_INT >= 30600:
            picture_data = SymbolConverter.get_picture_data(picture, None, layer.color,
                                                            layer.transparency_color, context=context)
            image_base64 = base64.b64encode(picture_data).decode('UTF-8')
            image_path = 'base64:{}'.format(image_base64)
        else:
            image_path = SymbolConverter.write_picture(picture, context.symbol_name,
                                                       context.get_picture_store_folder(),
                                                       None, layer.color,
                                                       layer.transparency_color, context=context)

        out = QgsRasterFillSymbolLayer(image_path)

        # convert to points, so that print layouts work nicely. It's a better match for Arc anyway
        width_in_pixels = layer.size * PictureUtils.width_pixels(picture.content)
        width_in_in_points = width_in_pixels / 96 * 72 / 2.5

        out.setWidth(context.convert_size(width_in_in_points))
        out.setWidthUnit(context.units)

        out.setAngle(ConversionUtils.convert_angle(layer.angle))

        out.setEnabled(layer.enabled)
        out.setLocked(layer.locked)
        if layer.symbol_level != 0xffffffff:
            out.setRenderingPass(layer.symbol_level)
        symbol.appendSymbolLayer(out)
        if isinstance(layer.outline, MultiLayerLineSymbol):
            # get all layers from outline
            SymbolConverter.append_SymbolLayer_to_QgsSymbolLayer(symbol, layer.outline, context)
        elif layer.outline:
            SymbolConverter.append_SymbolLayer_to_QgsSymbolLayer(symbol, layer.outline, context)

    @staticmethod
    def append_SimpleLineSymbolLayer(symbol, layer, context: Context):
        """
        Appends a SimpleLineSymbolLayer to a symbol
        """
        color = ColorConverter.color_to_qcolor(layer.color)
        out = QgsSimpleLineSymbolLayer(color)
        out.setEnabled(layer.enabled)
        out.setLocked(layer.locked)
        if layer.symbol_level != 0xffffffff:
            out.setRenderingPass(layer.symbol_level)
        out.setWidth(context.convert_size(context.fix_line_width(layer.width)))  # sometimes lines have negative width?
        out.setWidthUnit(context.units)
        # for arcgis, a pen width of 0 is not drawn, yet in QGIS it's a "hairline" size
        out.setPenStyle(ConversionUtils.symbol_pen_to_qpenstyle(layer.line_type) if layer.width > 0 else Qt.NoPen)
        # better match for ArcGIS rendering
        out.setPenCapStyle(Qt.RoundCap)
        out.setPenJoinStyle(Qt.RoundJoin)

        # better matching of null stroke color to QGIS symbology
        if out.color().alpha() == 0:
            out.setPenStyle(Qt.NoPen)

        if context.apply_conversion_tweaks and out.color().alpha() == 0 or out.penStyle() == Qt.NoPen:
            # avoid invisible layers
            return

        symbol.appendSymbolLayer(out)

    @staticmethod
    def append_SimpleLine3DSymbolLayer(symbol, layer: SimpleLine3DSymbol,
                                       context: Context):
        """
        Appends a SimpleLine3DSymbol to a symbol
        """
        if context.unsupported_object_callback:
            if context.layer_name:
                context.unsupported_object_callback(
                    '{}: 3D line was converted to a simple line'.format(context.layer_name),
                    level=Context.WARNING)
            elif context.symbol_name:
                context.unsupported_object_callback(
                    '{}: 3D line was converted to a simple line'.format(context.symbol_name), level=Context.WARNING)
            else:
                context.unsupported_object_callback('3D line was converted to a simple line', level=Context.WARNING)
        color = ColorConverter.color_to_qcolor(layer.color)
        out = QgsSimpleLineSymbolLayer(color)
        out.setEnabled(layer.enabled)
        out.setLocked(layer.locked)
        if layer.symbol_level != 0xffffffff:
            out.setRenderingPass(layer.symbol_level)
        out.setWidth(context.convert_size(context.fix_line_width(layer.width)))  # sometimes lines have negative width?
        out.setWidthUnit(context.units)
        out.setPenCapStyle(Qt.RoundCap)
        out.setPenJoinStyle(Qt.RoundJoin)

        # better matching of null stroke color to QGIS symbology
        if out.color().alpha() == 0:
            out.setPenStyle(Qt.NoPen)

        if context.apply_conversion_tweaks and out.color().alpha() == 0 or out.penStyle() == Qt.NoPen:
            # avoid invisible layers
            return

        symbol.appendSymbolLayer(out)

    @staticmethod
    def apply_template_to_LineSymbolLayer_custom_dash(template, layer, context: Context):
        """
        Applies a line template to a QgsSimpleLineSymbolLayer custom dash pattern
        """
        if not template.pattern_parts:
            return

        interval = context.convert_size(template.pattern_interval)

        dash_vector = []
        for part in template.pattern_parts:
            if part[0] == 0:
                # QGIS skips drawing a 0 part, so fake it
                dash_vector.append(0.000001)
            else:
                dash_vector.append(part[0] * interval)

            if part[1] == 0:
                # QGIS skips drawing a 0 part, so fake it
                dash_vector.append(0.000001)
            else:
                dash_vector.append(part[1] * interval)

        layer.setCustomDashVector(dash_vector)
        layer.setUseCustomDashPattern(True)
        layer.setCustomDashPatternUnit(context.units)

    @staticmethod
    def append_CartographicLineSymbolLayer(symbol, layer: CartographicLineSymbol, context: Context):
        """
        Appends a CartographicLineSymbolLayer to a symbol
        """
        color = ColorConverter.color_to_qcolor(layer.color)
        out = QgsSimpleLineSymbolLayer(color)
        out.setEnabled(layer.enabled)
        out.setLocked(layer.locked)
        if layer.symbol_level != 0xffffffff:
            out.setRenderingPass(layer.symbol_level)
        out.setWidth(context.convert_size(context.fix_line_width(layer.width)))  # sometimes lines have negative width?
        out.setWidthUnit(context.units)
        out.setPenJoinStyle(ConversionUtils.symbol_pen_to_qpenjoinstyle(layer.join))
        out.setPenCapStyle(ConversionUtils.symbol_pen_to_qpencapstyle(layer.cap))
        if layer.template is not None:
            SymbolConverter.apply_template_to_LineSymbolLayer_custom_dash(layer.template, out, context)

        # better matching of null stroke color to QGIS symbology
        if out.color().alpha() == 0:
            out.setPenStyle(Qt.NoPen)
        if layer.width <= 0:
            # for arcgis, a pen width of 0 is not drawn, yet in QGIS it's a "hairline" size
            out.setPenStyle(Qt.NoPen)

        # offset direction is flipped in arcgis world
        out.setOffset(-context.convert_size(layer.offset))
        out.setOffsetUnit(context.units)

        if context.apply_conversion_tweaks and out.color().alpha() == 0 or out.penStyle() == Qt.NoPen:
            # avoid invisible layers
            return

        symbol.appendSymbolLayer(out)

        if layer.decoration is not None:
            DecorationConverter.append_decorations(symbol, layer.decoration, context, enabled=layer.enabled,
                                                   locked=layer.locked)

    @staticmethod
    def append_TemplatedLineSymbolLayer(symbol,  # pylint: disable=too-many-statements,too-many-branches
                                        layer: Union[MarkerLineSymbol, HashLineSymbol],
                                        context: Context):
        """
        Appends a MarkerLineSymbolLayer or HashLineSymbol to a symbol
        """
        template = layer.template

        # first work out total length of pattern
        current_length = 0
        for t in template.pattern_parts:
            current_length += t[0]
            current_length += t[1]

        total_length = current_length * template.pattern_interval

        if isinstance(layer, MarkerLineSymbol):
            sub_symbol = SymbolConverter.Symbol_to_QgsSymbol(layer.pattern_marker, context)
            sub_symbol.setAngle(90)
        elif isinstance(layer, HashLineSymbol):
            sub_symbol = SymbolConverter.Symbol_to_QgsSymbol(layer.line, context)

        if len(template.pattern_parts) == 1 and \
                template.pattern_parts[0][1] == 0:  # pylint: disable=too-many-nested-blocks
            # special case! (Not described anywhere in ArcMap docs!!)
            # actually means "center of line segment"
            start_symbol = sub_symbol.clone()
            if isinstance(layer, MarkerLineSymbol):
                line = QgsMarkerLineSymbolLayer(True)
                start_symbol.setAngle(start_symbol.angle() - 90)
            else:
                if HAS_HASHED_LINE_SYMBOL_LAYER:
                    line = QgsHashedLineSymbolLayer(True)
                    line.setHashLength(layer.width)
                    line.setHashLengthUnit(QgsUnitTypes.RenderPoints)
                    line.setHashAngle(ConversionUtils.convert_angle(layer.angle - 90))
                else:
                    if context.unsupported_object_callback:
                        context.unsupported_object_callback(
                            '{}: Hashed line symbols require QGIS 3.8 or greater'.format(
                                context.layer_name or context.symbol_name),
                            Context.CRITICAL)
                        return
                    else:
                        raise NotImplementedException('Hashed line symbols require QGIS 3.8 or greater')

            line.setSubSymbol(start_symbol)
            line.setOffset(-context.convert_size(layer.offset))
            line.setOffsetUnit(context.units)

            if Qgis.QGIS_VERSION_INT >= 30900:
                from qgis.core import QgsTemplatedLineSymbolLayerBase  # pylint: disable=import-outside-toplevel
                if hasattr(QgsTemplatedLineSymbolLayerBase, 'SegmentCenter'):
                    line.setPlacement(QgsMarkerLineSymbolLayer.SegmentCenter)
                else:
                    line.setPlacement(QgsMarkerLineSymbolLayer.CentralPoint)
            else:
                # actually should be "Segment Center"
                line.setPlacement(QgsMarkerLineSymbolLayer.CentralPoint)

            line.setEnabled(layer.enabled)
            line.setLocked(layer.locked)
            if layer.symbol_level != 0xffffffff:
                line.setRenderingPass(layer.symbol_level)
            symbol.appendSymbolLayer(line)
        else:
            current_offset_from_start = 0
            for t in template.pattern_parts:
                if t[0]:
                    # symbol
                    start_symbol = sub_symbol.clone()
                    if isinstance(layer, MarkerLineSymbol):
                        line = QgsMarkerLineSymbolLayer(True)
                        start_symbol.setAngle(start_symbol.angle() - 90)
                    else:
                        if HAS_HASHED_LINE_SYMBOL_LAYER:
                            line = QgsHashedLineSymbolLayer(True)
                            line.setHashLength(layer.width)
                            line.setHashLengthUnit(QgsUnitTypes.RenderPoints)
                            line.setHashAngle(ConversionUtils.convert_angle(layer.angle - 90))
                        else:
                            if context.unsupported_object_callback:
                                context.unsupported_object_callback(
                                    '{}: Hashed line symbols require QGIS 3.8 or greater'.format(
                                        context.layer_name or context.symbol_name),
                                    Context.CRITICAL)
                                return
                            else:
                                raise NotImplementedException('Hashed line symbols require QGIS 3.8 or greater')

                    line.setSubSymbol(start_symbol)
                    line.setOffset(-context.convert_size(layer.offset))
                    line.setOffsetUnit(context.units)
                    line.setInterval(context.convert_size(total_length))
                    line.setIntervalUnit(context.units)
                    line.setOffsetAlongLine(
                        context.convert_size(current_offset_from_start + template.pattern_interval / 2))
                    line.setOffsetAlongLineUnit(context.units)

                    line.setEnabled(layer.enabled)
                    line.setLocked(layer.locked)
                    if layer.symbol_level != 0xffffffff:
                        line.setRenderingPass(layer.symbol_level)

                    symbol.appendSymbolLayer(line)

                    current_offset_from_start += template.pattern_interval * t[0]

                if t[1]:
                    # space
                    current_offset_from_start += template.pattern_interval * t[1]

        if layer.decoration is not None:
            DecorationConverter.append_decorations(symbol, layer.decoration, context, enabled=layer.enabled,
                                                   locked=layer.locked)

    @staticmethod
    def append_Marker3DSymbolLayer(symbol, layer: Marker3DSymbol,
                                   context: Context):
        """
        Appends a Marker3DSymbol to a symbol
        """
        if context.unsupported_object_callback:
            if context.layer_name:
                context.unsupported_object_callback(
                    '{}: 3D marker was converted to a simple marker'.format(context.layer_name), level=Context.WARNING)
            elif context.symbol_name:
                context.unsupported_object_callback(
                    '{}: 3D marker was converted to a simple marker'.format(context.symbol_name), level=Context.WARNING)
            else:
                context.unsupported_object_callback('3D marker was converted to a simple marker', level=Context.WARNING)
        picture = layer.picture
        if issubclass(picture.__class__, StdPicture):
            picture = picture.picture

        image = PictureUtils.colorize_picture(picture, layer.color)
        if context.embed_pictures:
            png_data = QBuffer()
            image.save(png_data, "png")
            picture_data = png_data.data()
            image_base64 = base64.b64encode(picture_data).decode('UTF-8')
            image_path = 'base64:{}'.format(image_base64)
        else:
            image_path = SymbolConverter.symbol_name_to_filename(context.symbol_name,
                                                                 context.get_picture_store_folder(), 'png')
            image.save(image_path)

        out = QgsRasterMarkerSymbolLayer(image_path, context.convert_size(layer.size_z))
        out.setSizeUnit(context.units)
        out.setEnabled(layer.enabled)
        out.setLocked(layer.locked)
        if layer.symbol_level != 0xffffffff:
            out.setRenderingPass(layer.symbol_level)
        symbol.appendSymbolLayer(out)

    @staticmethod
    def append_SimpleMarker3DSymbolLayer(symbol, layer: SimpleMarker3DSymbol, context: Context):
        """
        Appends a SimpleMarker3DSymbol to a symbol
        """
        if context.unsupported_object_callback:
            if context.layer_name:
                context.unsupported_object_callback(
                    '{}: 3D simple marker was converted to a simple marker'.format(context.layer_name),
                    level=Context.WARNING)
            elif context.symbol_name:
                context.unsupported_object_callback(
                    '{}: 3D simple marker was converted to a simple marker'.format(context.symbol_name),
                    level=Context.WARNING)
            else:
                context.unsupported_object_callback('3D simple marker was converted to a simple marker',
                                                    level=Context.WARNING)

        marker_type = SymbolConverter.marker_3d_type_to_qgis_type(layer.type)

        # convert size to approximate 2d size, based on ArcMap rendering
        out_size = max(1.5, 6 * math.log(layer.size_z) - 2.5)

        out = QgsSimpleMarkerSymbolLayer(marker_type, context.convert_size(out_size))
        out.setSizeUnit(context.units)

        color = ColorConverter.color_to_qcolor(layer.color)
        out.setColor(color)

        angle = ConversionUtils.convert_angle(layer.z_rotation)
        out.setAngle(angle)

        out.setEnabled(layer.enabled)
        out.setLocked(layer.locked)
        if layer.symbol_level != 0xffffffff:
            out.setRenderingPass(layer.symbol_level)

        out.setOffset(
            ConversionUtils.adjust_offset_for_rotation(
                QPointF(context.convert_size(layer.x_offset), -context.convert_size(layer.y_offset)),
                layer.z_rotation))
        out.setOffsetUnit(context.units)

        out.setStrokeStyle(Qt.NoPen)

        symbol.appendSymbolLayer(out)

    @staticmethod
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

    @staticmethod
    def marker_3d_type_to_qgis_type(symbol_type):
        """
        Converts simple 3d marker types to corresponding QGIS types
        """
        if symbol_type == SimpleMarker3DSymbol.TETRAHEDRON:
            return QgsSimpleMarkerSymbolLayerBase.Triangle
        elif symbol_type == SimpleMarker3DSymbol.CUBE:
            return QgsSimpleMarkerSymbolLayerBase.Square
        elif symbol_type in (SimpleMarker3DSymbol.CONE, SimpleMarker3DSymbol.CYLINDER, SimpleMarker3DSymbol.SPHERE,
                             SimpleMarker3DSymbol.SPHERE_FRAME):
            return QgsSimpleMarkerSymbolLayerBase.Circle
        elif symbol_type == SimpleMarker3DSymbol.DIAMOND:
            return QgsSimpleMarkerSymbolLayerBase.Diamond
        else:
            raise NotImplementedException('Marker type {} not implemented'.format(symbol_type))

    @staticmethod
    def append_SimpleMarkerSymbolLayer(symbol, layer: SimpleMarkerSymbol,
                                       context: Context):
        """
        Appends a SimpleMarkerSymbolLayer to a symbol
        """
        marker_type = SymbolConverter.marker_type_to_qgis_type(layer.type)
        out = QgsSimpleMarkerSymbolLayer(marker_type, context.convert_size(layer.size))
        out.setSizeUnit(context.units)

        color = ColorConverter.color_to_qcolor(layer.color)

        stroke_only_symbol = layer.type not in ('circle', 'square', 'diamond')
        if not stroke_only_symbol:
            out.setColor(color)
        else:
            out.setStrokeColor(color)

        out.setEnabled(layer.enabled)
        out.setLocked(layer.locked)
        if layer.symbol_level != 0xffffffff:
            out.setRenderingPass(layer.symbol_level)

        out.setOffset(QPointF(context.convert_size(layer.x_offset), -context.convert_size(layer.y_offset)))
        out.setOffsetUnit(context.units)

        if layer.outline_enabled:
            outline_color = ColorConverter.color_to_qcolor(layer.outline_color)
            if not stroke_only_symbol:
                out.setStrokeColor(outline_color)
                if not layer.color.is_null:
                    # Better match to how ESRI renders this if we divide the outline width by 2,
                    # because ESRI renders the stroke below the symbol. Maybe we should split this
                    # into two layers?
                    out.setStrokeWidth(context.convert_size(layer.outline_width / 2))
                else:
                    out.setStrokeWidth(context.convert_size(layer.outline_width))
                out.setStrokeWidthUnit(context.units)
                if layer.outline_width <= 0:
                    out.setStrokeStyle(Qt.NoPen)
            else:
                # for stroke-only symbols, we need to add the outline as an additional
                # symbol layer
                outline_layer = QgsSimpleMarkerSymbolLayer(marker_type, context.convert_size(layer.size))
                outline_layer.setSizeUnit(context.units)
                outline_layer.setStrokeColor(outline_color)
                outline_layer.setStrokeWidth(context.convert_size(context.fix_line_width(layer.outline_width)))
                outline_layer.setStrokeWidthUnit(context.units)
                symbol.appendSymbolLayer(outline_layer)
        elif not stroke_only_symbol:
            out.setStrokeStyle(Qt.NoPen)

        symbol.appendSymbolLayer(out)

    @staticmethod
    def append_ArrowMarkerSymbolLayer(symbol, layer: ArrowMarkerSymbol,
                                      context: Context):
        """
        Appends a ArrowMarkerSymbolLayer to a symbol
        """
        out = QgsEllipseSymbolLayer()
        out.setSymbolName('triangle')
        out.setStrokeStyle(Qt.NoPen)

        out.setSymbolHeight(context.convert_size(layer.size))
        out.setSymbolHeightUnit(context.units)
        out.setSymbolWidth(context.convert_size(layer.width))
        out.setSymbolWidthUnit(context.units)

        color = ColorConverter.color_to_qcolor(layer.color)
        out.setColor(color)
        out.setStrokeColor(color)  # why not, makes the symbol a bit easier to modify in qgis

        out.setOffset(
            ConversionUtils.adjust_offset_for_rotation(
                QPointF(context.convert_size(layer.x_offset), -context.convert_size(layer.y_offset)),
                layer.angle))
        out.setOffsetUnit(context.units)

        angle = 90 - layer.angle
        if angle <= -180:
            angle += 360
        if angle > 180:
            angle -= 360
        out.setAngle(angle)

        out.setEnabled(layer.enabled)
        out.setLocked(layer.locked)
        if layer.symbol_level != 0xffffffff:
            out.setRenderingPass(layer.symbol_level)

        symbol.appendSymbolLayer(out)

    ESRI_FONTS_TO_QGIS_MARKERS = {
        'ESRI Default Marker': {
            32: None,
            33: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle},
            34: {'shape': QgsSimpleMarkerSymbolLayerBase.Square},
            35: {'shape': QgsSimpleMarkerSymbolLayerBase.EquilateralTriangle},
            36: {'shape': QgsSimpleMarkerSymbolLayerBase.Pentagon},
            37: {'shape': QgsSimpleMarkerSymbolLayerBase.Hexagon},
            40: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                 'outline_only': True},
            41: {'shape': QgsSimpleMarkerSymbolLayerBase.Square,
                 'outline_only': True},
            42: {'shape': QgsSimpleMarkerSymbolLayerBase.EquilateralTriangle,
                 'outline_only': True},
            43: {'shape': QgsSimpleMarkerSymbolLayerBase.Pentagon,
                 'outline_only': True},
            44: {'shape': QgsSimpleMarkerSymbolLayerBase.Hexagon,
                 'outline_only': True},
            46: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                 'outline_only': True,
                 'central_overlay': QgsSimpleMarkerSymbolLayerBase.Circle},
            47: {'shape': QgsSimpleMarkerSymbolLayerBase.Square,
                 'outline_only': True,
                 'central_overlay': QgsSimpleMarkerSymbolLayerBase.Circle},
            48: {'shape': QgsSimpleMarkerSymbolLayerBase.EquilateralTriangle,
                 'outline_only': True,
                 'central_overlay': QgsSimpleMarkerSymbolLayerBase.Circle},
            49: {'shape': QgsSimpleMarkerSymbolLayerBase.Pentagon,
                 'outline_only': True,
                 'central_overlay': QgsSimpleMarkerSymbolLayerBase.Circle},
            50: {'shape': QgsSimpleMarkerSymbolLayerBase.Hexagon,
                 'outline_only': True,
                 'central_overlay': QgsSimpleMarkerSymbolLayerBase.Circle},
            53: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                 'outline_only': True,
                 'central_overlay': QgsSimpleMarkerSymbolLayerBase.Square},
            54: {'shape': QgsSimpleMarkerSymbolLayerBase.Square,
                 'outline_only': True,
                 'central_overlay': QgsSimpleMarkerSymbolLayerBase.Square},
            55: {'shape': QgsSimpleMarkerSymbolLayerBase.EquilateralTriangle,
                 'outline_only': True,
                 'central_overlay': QgsSimpleMarkerSymbolLayerBase.Square},
            56: {'shape': QgsSimpleMarkerSymbolLayerBase.Pentagon,
                 'outline_only': True,
                 'central_overlay': QgsSimpleMarkerSymbolLayerBase.Square},
            57: {'shape': QgsSimpleMarkerSymbolLayerBase.Hexagon,
                 'outline_only': True,
                 'central_overlay': QgsSimpleMarkerSymbolLayerBase.Square},
            60: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                 'outline_only': True,
                 'overlay': QgsSimpleMarkerSymbolLayerBase.SemiCircle,
                 'overlay_angle': 90
                 },
            61: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                 'outline_only': True,
                 'overlay': QgsSimpleMarkerSymbolLayerBase.Line},
            62: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                 'outline_only': True,
                 'overlay': QgsSimpleMarkerSymbolLayerBase.Cross},
            63: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                 'outline_only': True,
                 'overlay': QgsSimpleMarkerSymbolLayerBase.Cross,
                 'overlay_angle': 45},
            65: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                 'shape_size_factor': 8.129480 / 12.129480,
                 'outline_only': True,
                 'overlay': QgsSimpleMarkerSymbolLayerBase.Cross,
                 'overlay_size_factor': 13.249480 / 8.129480},
            66: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                 'shape_size_factor': 0.8548989734102369,
                 'outline_only': True,
                 'overlay': QgsSimpleMarkerSymbolLayerBase.Cross,
                 'overlay_size_factor': 13.249480 / 8.129480,
                 'overlay_angle': 45},
            72: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                 'outline_only': True,
                 'stroke_size_factor': 2.813333333333333,
                 'central_overlay': QgsSimpleMarkerSymbolLayerBase.Circle,
                 'overlay_size_factor': 1.3654742518282246},
            73: {'shape': QgsSimpleMarkerSymbolLayerBase.EquilateralTriangle,
                 'outline_only': True,
                 'stroke_size_factor': 1.5143456548019383,
                 'central_overlay': QgsSimpleMarkerSymbolLayerBase.EquilateralTriangle,
                 'overlay_size_factor': 0.26396286832045446,
                 'overlay_y_offset_factor': 1.3703703703703705},
            74: {'shape': QgsSimpleMarkerSymbolLayerBase.Square,
                 'outline_only': True,
                 'shape_size_factor': 0.8895253547555213,
                 'stroke_size_factor': 1.9410120363760561,
                 'central_overlay': QgsSimpleMarkerSymbolLayerBase.Square,
                 'overlay_size_factor': 1.6658045385884221},
            75: {'shape': QgsSimpleMarkerSymbolLayerBase.Pentagon,
                 'outline_only': True,
                 'shape_size_factor': 1.0098932629689819,
                 'stroke_size_factor': 1.9410120363760561,
                 'central_overlay': QgsSimpleMarkerSymbolLayerBase.Pentagon,
                 'overlay_size_factor': 0.3228621997955166,
                 'overlay_y_offset': 0.14955468922886098},
            76: {'shape': QgsSimpleMarkerSymbolLayerBase.Hexagon,
                 'outline_only': True,
                 'shape_size_factor': 1.0098932629689819,
                 'stroke_size_factor': 1.9410120363760561,
                 'central_overlay': QgsSimpleMarkerSymbolLayerBase.Hexagon,
                 'overlay_size_factor': 0.3228621997955166,
                 'overlay_angle': 90},
            87: {'ellipse_marker_type': 'diamond',
                 'outline_only': True,
                 'width_factor': 2.620000 / 13.990840,
                 'height_factor': 4.590840 / 13.990840},
            88: {'ellipse_marker_type': 'diamond',
                 'width_factor': 2.620000 / 13.990840,
                 'height_factor': 4.590840 / 13.990840},
            89: {'ellipse_marker_type': 'diamond',
                 'outline_only': True,
                 'width_factor': 2.260000 / 13.990840,
                 'height_factor': 3.930840 / 13.990840,
                 'stroke_scale': 0.991667 / 0.791667},
            94: {'shape': QgsSimpleMarkerSymbolLayerBase.Star},
            95: {'shape': QgsSimpleMarkerSymbolLayerBase.Star,
                 'outline_only': True},
        }
    }

    if Qgis.QGIS_VERSION_INT >= 31800:
        ESRI_FONTS_TO_QGIS_MARKERS['ESRI Default Marker'].update({
            38: {
                'shape': QgsSimpleMarkerSymbolLayerBase.Octagon,
            },
            39: {
                'shape': QgsSimpleMarkerSymbolLayerBase.SquareWithCorners,
            },
            45: {
                'shape': QgsSimpleMarkerSymbolLayerBase.Octagon,
                'outline_only': True
            },
            51: {'shape': QgsSimpleMarkerSymbolLayerBase.Octagon,
                 'outline_only': True,
                 'central_overlay': QgsSimpleMarkerSymbolLayerBase.Circle},
            52: {'shape': QgsSimpleMarkerSymbolLayerBase.SquareWithCorners,
                 'outline_only': True,
                 'central_overlay': QgsSimpleMarkerSymbolLayerBase.Circle},
            58: {'shape': QgsSimpleMarkerSymbolLayerBase.Octagon,
                 'outline_only': True,
                 'central_overlay': QgsSimpleMarkerSymbolLayerBase.Square},
            59: {'shape': QgsSimpleMarkerSymbolLayerBase.SquareWithCorners,
                 'outline_only': True,
                 'central_overlay': QgsSimpleMarkerSymbolLayerBase.Square},
            77: {'shape': QgsSimpleMarkerSymbolLayerBase.Octagon,
                 'outline_only': True,
                 'shape_size_factor': 1.0098932629689819,
                 'stroke_size_factor': 1.9410120363760561,
                 'central_overlay': QgsSimpleMarkerSymbolLayerBase.Octagon,
                 'overlay_size_factor': 0.3228621997955166},
            78: {'shape': QgsSimpleMarkerSymbolLayerBase.SquareWithCorners,
                 'outline_only': True,
                 'shape_size_factor': 1.0098932629689819,
                 'stroke_size_factor': 1.0876792732278202,
                 'central_overlay': QgsSimpleMarkerSymbolLayerBase.SquareWithCorners,
                 'overlay_size_factor': 0.3228621997955166},
            106: {
                'shape': QgsSimpleMarkerSymbolLayerBase.AsteriskFill,
                'outline_only': True
            },
            107: {
                'shape': QgsSimpleMarkerSymbolLayerBase.AsteriskFill,
            },
        })

    ALIAS_FONTS = {
        'ESRI AMFM Water': {38: {'font_name': 'ESRI Default Marker',
                                 'character': 33},
                            84: {'font_name': 'ESRI Default Marker',
                                 'character': 33},
                            108: {'font_name': 'ESRI Default Marker',
                                  'character': 33}},
        'ESRI Geometric Symbols': {
            34: {'font_name': 'ESRI Default Marker',
                 'character': 33,
                 'vertical_offset_factor': 0},
            35: {'font_name': 'ESRI Default Marker',
                 'character': 33,
                 'vertical_offset_factor': 0},
        }
    }

    REPLACE_FONTS = {
        'SIGEOM_SYMBOL2': {
            61473: {'font_name': 'SIGEOM_SYMBOL2', 'unicode': 33},
            61474: {'font_name': 'SIGEOM_SYMBOL2', 'unicode': 34},
            61475: {'font_name': 'SIGEOM_SYMBOL2', 'unicode': 35},
            61476: {'font_name': 'SIGEOM_SYMBOL2', 'unicode': 36},
            61477: {'font_name': 'SIGEOM_SYMBOL2', 'unicode': 37},
            61478: {'font_name': 'SIGEOM_SYMBOL2', 'unicode': 38},
            61479: {'font_name': 'SIGEOM_SYMBOL2', 'unicode': 39},
            61480: {'font_name': 'SIGEOM_SYMBOL2', 'unicode': 40},
            61481: {'font_name': 'SIGEOM_SYMBOL2', 'unicode': 41},
            61482: {'font_name': 'SIGEOM_SYMBOL2', 'unicode': 42},
            61483: {'font_name': 'SIGEOM_SYMBOL2', 'unicode': 43},
            61484: {'font_name': 'SIGEOM_SYMBOL2', 'unicode': 44},
            61485: {'font_name': 'SIGEOM_SYMBOL2', 'unicode': 45},
            61486: {'font_name': 'SIGEOM_SYMBOL2', 'unicode': 46},
            61487: {'font_name': 'SIGEOM_SYMBOL2', 'unicode': 47},
            61488: {'font_name': 'SIGEOM_SYMBOL2', 'unicode': 48},
            61489: {'font_name': 'SIGEOM_SYMBOL2', 'unicode': 49},
            61490: {'font_name': 'SIGEOM_SYMBOL2', 'unicode': 50},
            61491: {'font_name': 'SIGEOM_SYMBOL2', 'unicode': 51},
            61492: {'font_name': 'SIGEOM_SYMBOL2', 'unicode': 52},
            61493: {'font_name': 'SIGEOM_SYMBOL2', 'unicode': 53},
            61494: {'font_name': 'SIGEOM_SYMBOL2', 'unicode': 54},
            61495: {'font_name': 'SIGEOM_SYMBOL2', 'unicode': 55},
            61496: {'font_name': 'SIGEOM_SYMBOL2', 'unicode': 56},
            61497: {'font_name': 'SIGEOM_SYMBOL2', 'unicode': 57},
        }
    }

    @staticmethod
    def can_convert_esri_font_character_to_simple_marker(font_name: str, character: int) -> bool:
        """
        Returns True if a font marker with the specified name and character can be converted to a simple marker
        """
        if font_name in SymbolConverter.ALIAS_FONTS and character in SymbolConverter.ALIAS_FONTS[font_name]:
            alias = SymbolConverter.ALIAS_FONTS[font_name][character]
            font_name = alias['font_name']
            character = alias['character']

        return character in SymbolConverter.ESRI_FONTS_TO_QGIS_MARKERS.get(font_name, {})

    @staticmethod
    def replace_char_if_needed(font_name: str, character: int) -> Tuple[str, int]:
        """
        Replaces font name and unicode using REPLACE_FONTS
        """
        if font_name in SymbolConverter.REPLACE_FONTS:
            if character in SymbolConverter.REPLACE_FONTS[font_name]:
                conversion = SymbolConverter.REPLACE_FONTS[font_name][character]
                font_name = conversion['font_name']
                character = conversion['unicode']
        return font_name, character

    @staticmethod
    def append_CharacterMarkerSymbolLayer(symbol, layer: CharacterMarkerSymbol, context: Context):
        """
        Appends a CharacterMarkerSymbolLayer to a symbol
        """
        font, unicode = SymbolConverter.replace_char_if_needed(layer.font, layer.unicode)

        if context.convert_esri_fonts_to_simple_markers and SymbolConverter.can_convert_esri_font_character_to_simple_marker(
                font, unicode):
            SymbolConverter.append_CharacterMarkerSymbolLayerAsSimpleMarker(symbol, layer, context)
        elif context.convert_fonts:
            SymbolConverter.append_CharacterMarkerSymbolLayerAsSvg(symbol, layer, context)
        else:
            SymbolConverter.append_CharacterMarkerSymbolLayerAsFont(symbol, layer, context)

    @staticmethod
    def append_CharacterMarker3DSymbolLayer(symbol, layer: CharacterMarker3DSymbol, context: Context):
        """
        Appends a CharacterMarker3DSymbol  to a symbol
        """
        if context.unsupported_object_callback:
            if context.layer_name:
                context.unsupported_object_callback(
                    '{}: 3D character marker was converted to a 2d character marker'.format(context.layer_name),
                    level=Context.WARNING)
            elif context.symbol_name:
                context.unsupported_object_callback(
                    '{}: 3D character marker was converted to a 2d character marker'.format(context.symbol_name),
                    level=Context.WARNING)
            else:
                context.unsupported_object_callback('3D character marker was converted to a 2d character marker',
                                                    level=Context.WARNING)
        if context.convert_fonts:
            SymbolConverter.append_CharacterMarkerSymbolLayerAsSvg(symbol, layer.character_marker_symbol, context)
        else:
            SymbolConverter.append_CharacterMarkerSymbolLayerAsFont(symbol, layer.character_marker_symbol, context)

    @staticmethod
    def append_CharacterMarkerSymbolLayerAsSimpleMarker(symbol,  # pylint: disable=too-many-locals,too-many-statements,too-many-branches
                                                        layer: CharacterMarkerSymbol,
                                                        context: Context):
        """
        Appends a CharacterMarkerSymbolLayer to a symbol, converting the symbol to a simple qgis marker
        """
        font_name, character = SymbolConverter.replace_char_if_needed(layer.font, layer.unicode)

        vertical_offset_factor = 0
        if font_name in SymbolConverter.ALIAS_FONTS and character in SymbolConverter.ALIAS_FONTS[font_name]:
            alias = SymbolConverter.ALIAS_FONTS[font_name][character]
            font_name = alias['font_name']
            character = alias['character']
            vertical_offset_factor = alias.get('vertical_offset_factor', 0)

        conversion_properties = SymbolConverter.ESRI_FONTS_TO_QGIS_MARKERS[font_name][character]
        if conversion_properties is None:
            if symbol.symbolLayerCount():
                # don't add an empty shell
                return

            # add an effectively "null" symbol
            out = QgsSimpleMarkerSymbolLayer(QgsSimpleMarkerSymbolLayerBase.Circle, 8)
            out.setColor(QColor(255, 255, 255, 0))
            out.setStrokeStyle(Qt.NoPen)
            out.setLocked(True)
            out.setEnabled(layer.enabled)
            symbol.appendSymbolLayer(out)
            return

        angle_offset = 0
        outline_stroke_width = 1
        size_scale_factor = 1
        if 'shape' in conversion_properties:
            marker_type = conversion_properties.get('shape', QgsSimpleMarkerSymbolLayerBase.Square)

            if marker_type in (QgsSimpleMarkerSymbolLayerBase.Circle,
                               QgsSimpleMarkerSymbolLayerBase.Square,
                               QgsSimpleMarkerSymbolLayerBase.EquilateralTriangle,
                               QgsSimpleMarkerSymbolLayerBase.Pentagon):
                simple_size = (1.47272 * layer.size) / 2.0
            elif marker_type == QgsSimpleMarkerSymbolLayerBase.Hexagon:
                simple_size = (1.47272 * layer.size * 4.178160 / 4.418160) / 2.0
            elif marker_type == QgsSimpleMarkerSymbolLayerBase.Star:
                simple_size = (1.47272 * layer.size * 12.327200 / 14.727200) / 2.0
            elif Qgis.QGIS_VERSION_INT >= 31800:
                if marker_type in (QgsSimpleMarkerSymbolLayerBase.Octagon,
                                   QgsSimpleMarkerSymbolLayerBase.SquareWithCorners):
                    simple_size = (1.3632460 * layer.size) / 2.0
                elif marker_type == QgsSimpleMarkerSymbolLayerBase.AsteriskFill:
                    simple_size = (1.3632460 * layer.size) / 2.0

            simple_size *= conversion_properties.get('shape_size_factor', 1)

            out = QgsSimpleMarkerSymbolLayer(marker_type, context.convert_size(simple_size))
            stroke_only_symbol = not QgsSimpleMarkerSymbolLayerBase.shapeIsFilled(
                marker_type) or conversion_properties.get('outline_only', False)

            y_offset = layer.y_offset + vertical_offset_factor * simple_size

            SHAPE_BASED_OFFSET = {
                QgsSimpleMarkerSymbolLayerBase.EquilateralTriangle: 1.8 / 14.7272,
                QgsSimpleMarkerSymbolLayerBase.Pentagon: 0.2 / 4.418160,
                QgsSimpleMarkerSymbolLayerBase.Star: 0.600000 / 12.327200
            }

            if marker_type in SHAPE_BASED_OFFSET:
                y_offset -= simple_size * SHAPE_BASED_OFFSET[marker_type]

            if marker_type == QgsSimpleMarkerSymbolLayerBase.Hexagon:
                angle_offset += 90

            if marker_type == QgsSimpleMarkerSymbolLayerBase.Star:
                outline_stroke_width = (layer.size / 48) * 1.016667 / 0.416667
            else:
                outline_stroke_width = layer.size / 48

            outline_stroke_width *= conversion_properties.get('stroke_size_factor', 1)

            if marker_type != QgsSimpleMarkerSymbolLayerBase.Star:
                size_scale_factor = 10.781760 / 11.781760

        elif 'ellipse_marker_type' in conversion_properties:
            symbol_name = conversion_properties['ellipse_marker_type']

            simple_size = (1.47272 * layer.size) / 2.0

            out = QgsEllipseSymbolLayer()
            out.setSymbolName(symbol_name)
            out.setSymbolWidth(simple_size * conversion_properties.get('width_factor', 1))
            out.setSymbolHeight(simple_size * conversion_properties.get('height_factor', 1))

            stroke_only_symbol = conversion_properties.get('outline_only', False)
            y_offset = layer.y_offset + vertical_offset_factor * simple_size
            outline_stroke_width = layer.size / 24

            outline_stroke_width *= conversion_properties.get('stroke_scale', 1)

        out.setSizeUnit(context.units)

        color = ColorConverter.color_to_qcolor(layer.color)
        out.setPenJoinStyle(Qt.MiterJoin)

        out.setEnabled(layer.enabled)
        out.setLocked(layer.locked or character == 32)
        if layer.symbol_level != 0xffffffff:
            out.setRenderingPass(layer.symbol_level)

        angle = ConversionUtils.convert_angle(layer.angle)
        angle += angle_offset

        out.setAngle(angle)

        out.setOffset(
            ConversionUtils.adjust_offset_for_rotation(
                QPointF(context.convert_size(layer.x_offset), -context.convert_size(y_offset)),
                angle))

        out.setOffsetUnit(context.units)

        if not stroke_only_symbol:
            out.setStrokeStyle(Qt.NoPen)

        appended_to_prev_layer = False
        if not stroke_only_symbol:
            out.setColor(color)
        else:
            if symbol.symbolLayerCount() > 0:
                prev_layer = symbol.symbolLayer(symbol.symbolLayerCount() - 1)

                # in ESRI land people often place outline only versions of font markers over the filled
                # versions in order to get an outline
                can_condense_to_simple_marker = isinstance(out, QgsSimpleMarkerSymbolLayer) and \
                                                isinstance(prev_layer, QgsSimpleMarkerSymbolLayer) and \
                                                out.type() == prev_layer.type() and \
                                                prev_layer.size() == out.size() and prev_layer.angle() == out.angle() and \
                                                prev_layer.offset() == out.offset() and prev_layer.strokeStyle() == Qt.NoPen

                can_condense_to_ellipse_marker = isinstance(out, QgsEllipseSymbolLayer) and \
                                                 isinstance(prev_layer, QgsEllipseSymbolLayer) and \
                                                 out.symbolName() == prev_layer.symbolName() and \
                                                 prev_layer.symbolHeight() == out.symbolHeight() and \
                                                 prev_layer.symbolWidth() == out.symbolWidth() and \
                                                 prev_layer.angle() == out.angle() and \
                                                 prev_layer.offset() == out.offset() and \
                                                 prev_layer.strokeStyle() == Qt.NoPen

                if can_condense_to_simple_marker:
                    # effectively the same symbol, just an outline version of it! Let's make the results nice
                    # and QGIS-esque by just adding the stroke to the previous layer instead of creating a brand
                    # new layer
                    appended_to_prev_layer = True
                    prev_layer.setStrokeStyle(Qt.SolidLine)
                    prev_layer.setStrokeColor(color)
                    prev_layer.setStrokeWidth(context.convert_size(layer.size / 48))
                    prev_layer.setStrokeWidthUnit(context.units)
                elif can_condense_to_ellipse_marker:
                    # effectively the same symbol, just an outline version of it! Let's make the results nice
                    # and QGIS-esque by just adding the stroke to the previous layer instead of creating a brand
                    # new layer
                    appended_to_prev_layer = True
                    prev_layer.setStrokeStyle(Qt.SolidLine)
                    prev_layer.setStrokeColor(color)
                    prev_layer.setStrokeWidth(context.convert_size(layer.size / 24))
                    prev_layer.setStrokeWidthUnit(context.units)

            if not appended_to_prev_layer:
                out.setStrokeColor(color)

        if not appended_to_prev_layer and conversion_properties.get('outline_only', False):
            out.setColor(QColor(255, 255, 255, 0))
            out.setStrokeWidth(context.convert_size(outline_stroke_width))
            out.setStrokeWidthUnit(context.units)
            out.setSize(out.size() * size_scale_factor)

        if not appended_to_prev_layer:
            symbol.appendSymbolLayer(out)

        if 'overlay' in conversion_properties:
            # Add overlay layer
            marker_type = conversion_properties['overlay']

            overlay_size = out.size() * conversion_properties.get('overlay_size_factor', 1)

            overlay = QgsSimpleMarkerSymbolLayer(marker_type, overlay_size)
            overlay.setSizeUnit(context.units)

            stroke_only_symbol = not QgsSimpleMarkerSymbolLayerBase.shapeIsFilled(marker_type)

            color = ColorConverter.color_to_qcolor(layer.color)

            if not stroke_only_symbol:
                overlay.setColor(color)
                out.setStrokeStyle(Qt.NoPen)
            else:
                overlay.setStrokeColor(color)

            if marker_type == QgsSimpleMarkerSymbolLayerBase.Star:
                overlay.setStrokeWidth(context.convert_size(layer.size / 48) * 1.016667 / 0.416667)
            else:
                overlay.setStrokeWidth(context.convert_size(layer.size / 48))
            overlay.setStrokeWidthUnit(context.units)

            overlay.setEnabled(layer.enabled)
            overlay.setLocked(layer.locked or character == 32)
            if layer.symbol_level != 0xffffffff:
                overlay.setRenderingPass(layer.symbol_level)

            angle = ConversionUtils.convert_angle(layer.angle)
            angle += conversion_properties.get('overlay_angle', 0)

            overlay.setAngle(angle)

            overlay.setOffset(
                ConversionUtils.adjust_offset_for_rotation(
                    QPointF(context.convert_size(layer.x_offset), -context.convert_size(y_offset)),
                    angle))

            overlay.setOffset(QPointF(overlay.offset().x(),
                                      overlay.offset().y() * conversion_properties.get('overlay_y_offset_factor', 0)))

            overlay.setOffsetUnit(context.units)
            symbol.appendSymbolLayer(overlay)

        if 'central_overlay' in conversion_properties:
            # Add central dot symbol layer
            marker_type = conversion_properties['central_overlay']

            simple_size = (1.47272 * layer.size) / 2.0
            if marker_type == QgsSimpleMarkerSymbolLayerBase.Circle:
                simple_size *= 2.901760 / 11.781760
            elif marker_type == QgsSimpleMarkerSymbolLayerBase.Square:
                simple_size *= 2.041760 / 11.781760

            simple_size *= conversion_properties.get('overlay_size_factor', 1)

            out = QgsSimpleMarkerSymbolLayer(marker_type, context.convert_size(simple_size))
            out.setSizeUnit(context.units)
            color = ColorConverter.color_to_qcolor(layer.color)
            out.setColor(color)

            out.setEnabled(layer.enabled)
            out.setLocked(layer.locked or character == 32)
            if layer.symbol_level != 0xffffffff:
                out.setRenderingPass(layer.symbol_level)

            angle = ConversionUtils.convert_angle(layer.angle)
            angle += conversion_properties.get('overlay_angle', 0)

            out.setAngle(angle)

            out.setOffset(
                ConversionUtils.adjust_offset_for_rotation(
                    QPointF(context.convert_size(layer.x_offset), -context.convert_size(y_offset)),
                    angle))

            if 'overlay_y_offset' in conversion_properties:
                out.setOffset(QPointF(out.offset().x(),
                                      out.size() * conversion_properties['overlay_y_offset']))

            out.setOffset(
                QPointF(out.offset().x(), out.offset().y() * conversion_properties.get('overlay_y_offset_factor', 1)))

            out.setOffsetUnit(context.units)
            out.setStrokeStyle(Qt.NoPen)
            symbol.appendSymbolLayer(out)

    @staticmethod
    def append_CharacterMarkerSymbolLayerAsSvg(symbol, layer,  # pylint: disable=too-many-locals,too-many-statements
                                               context: Context):
        """
        Appends a CharacterMarkerSymbolLayer to a symbol, rendering the font character
        to an SVG file.
        """
        font_family, unicode = SymbolConverter.replace_char_if_needed(layer.font, layer.unicode)

        if context.unsupported_object_callback and font_family not in QFontDatabase().families():
            context.unsupported_object_callback('Font {} not available on system'.format(font_family),
                                                level=Context.WARNING)

        character = chr(unicode)
        color = ColorConverter.color_to_qcolor(layer.color)
        angle = ConversionUtils.convert_angle(layer.angle)

        font = QFont(font_family)
        font.setPointSizeF(layer.size)

        # Using the rect of a painter path gives better results then using font metrics
        path = QPainterPath()
        path.setFillRule(Qt.WindingFill)
        path.addText(0, 0, font, character)

        rect = path.boundingRect()

        font_bounding_rect = QFontMetricsF(font).boundingRect(character)

        # adjust size -- marker size in esri is the font size, svg marker size in qgis is the svg rect size
        scale = rect.width() / font_bounding_rect.width() if font_bounding_rect.width() else 1

        gen = QSvgGenerator()
        svg_path = SymbolConverter.symbol_name_to_filename(context.symbol_name, context.get_picture_store_folder(),
                                                           'svg')
        gen.setFileName(svg_path)
        gen.setViewBox(rect)

        painter = QPainter(gen)
        painter.setFont(font)

        # todo -- size!

        painter.setBrush(QBrush(QColor(255, 0, 0)))
        painter.setPen(Qt.NoPen)
        painter.drawPath(path)
        painter.end()

        with open(svg_path, 'r', encoding='utf8') as f:
            t = f.read()

        t = t.replace('#ff0000', 'param(fill)')
        t = t.replace('fill-opacity="1" ', 'fill-opacity="param(fill-opacity)"')
        t = t.replace('stroke="none"',
                      'stroke="param(outline)" stroke-opacity="param(outline-opacity) 1" stroke-width="param(outline-width) 0"')

        if context.embed_pictures:
            svg_content = base64.b64encode(t.encode('UTF-8')).decode('UTF-8')
            svg_path = 'base64:{}'.format(svg_content)
        else:
            with open(svg_path, 'w', encoding='utf8') as f:
                f.write(t)
            svg_path = context.convert_path(svg_path)

        out = QgsSvgMarkerSymbolLayer(svg_path)

        out.setSizeUnit(context.units)
        # esri symbol sizes are for height, QGIS are for width
        if out.defaultAspectRatio() != 1 and out.defaultAspectRatio() != 0:
            out.setSize(context.convert_size(scale * rect.width()) / out.defaultAspectRatio())
        else:
            out.setSize(context.convert_size(scale * rect.width()))
        out.setAngle(angle)
        out.setFillColor(color)
        out.setStrokeWidth(0)

        out.setEnabled(layer.enabled)
        out.setLocked(layer.locked)
        if layer.symbol_level != 0xffffffff:
            out.setRenderingPass(layer.symbol_level)

        out.setOffset(
            ConversionUtils.adjust_offset_for_rotation(
                QPointF(context.convert_size(layer.x_offset), -context.convert_size(layer.y_offset)),
                layer.angle))
        out.setOffsetUnit(context.units)

        symbol.appendSymbolLayer(out)

    @staticmethod
    def append_CharacterMarkerSymbolLayerAsFont(symbol, layer, context: Context):
        """
        Appends a CharacterMarkerSymbolLayer to a symbol, using QGIS font marker symbols
        """
        font_family, unicode = SymbolConverter.replace_char_if_needed(layer.font, layer.unicode)

        if context.unsupported_object_callback and font_family not in QFontDatabase().families():
            context.unsupported_object_callback('Font {} not available on system'.format(font_family),
                                                level=Context.WARNING)

        character = chr(unicode)
        color = ColorConverter.color_to_qcolor(layer.color)
        angle = ConversionUtils.convert_angle(layer.angle)

        # we need to calculate the character bounding box, as ESRI font marker symbols are rendered centered
        # on the character's bounding box (not the overall font metrics, like QGIS does)
        font = QFont(font_family)
        font.setPointSizeF(layer.size)
        font_metrics = QFontMetricsF(font)

        # This seems to give best conversion match to ESRI - vs tightBoundingRect
        rect = font_metrics.boundingRect(character)
        # note the font_metrics.width/ascent adjustments are here to reverse how QGIS offsets font markers
        x_offset_points = rect.center().x() - font_metrics.width(character) / 2.0
        y_offset_points = -rect.center().y() - font_metrics.ascent() / 2.0

        out = QgsFontMarkerSymbolLayer(font_family, character, context.convert_size(layer.size), color, angle)
        out.setSizeUnit(context.units)

        out.setEnabled(layer.enabled)
        out.setLocked(layer.locked)
        if layer.symbol_level != 0xffffffff:
            out.setRenderingPass(layer.symbol_level)

        temp_offset = ConversionUtils.adjust_offset_for_rotation(QPointF(layer.x_offset, -layer.y_offset), layer.angle)
        out.setOffset(QPointF(context.convert_size(temp_offset.x() + x_offset_points),
                              context.convert_size(temp_offset.y() + y_offset_points)))
        out.setOffsetUnit(context.units)

        symbol.appendSymbolLayer(out)

    @staticmethod
    def append_PictureMarkerSymbolLayer(symbol,  # pylint: disable=too-many-branches
                                        layer: PictureMarkerSymbol,
                                        context: Context):
        """
        Appends a PictureMarkerSymbolLayer to a symbol
        """
        picture = layer.picture
        if not picture:
            return

        if issubclass(picture.__class__, StdPicture):
            picture = picture.picture

        if issubclass(picture.__class__, EmfPicture) or (
                issubclass(picture.__class__, BmpPicture) and picture.format == BmpPicture.FORMAT_EMF) \
                or Qgis.QGIS_VERSION_INT < 30600:
            if issubclass(picture.__class__, EmfPicture) or (
                    issubclass(picture.__class__, BmpPicture) and picture.format == BmpPicture.FORMAT_EMF):
                path = SymbolConverter.symbol_name_to_filename(context.symbol_name, context.get_picture_store_folder(),
                                                               'emf')
                with open(path, 'wb') as f:
                    f.write(picture.content)

                svg_path = SymbolConverter.symbol_name_to_filename(context.symbol_name,
                                                                   context.get_picture_store_folder(), 'svg')
                SymbolConverter.emf_to_svg(path, svg_path, inkscape_path=context.inkscape_path, context=context)

                if not os.path.exists(svg_path):
                    if context.unsupported_object_callback:
                        context.unsupported_object_callback(
                            '{}: Conversion of EMF picture failed'.format(context.layer_name or context.symbol_name),
                            level=Context.CRITICAL)

                if context.embed_pictures and os.path.exists(svg_path):
                    with open(svg_path, 'rb') as svg_file:
                        svg_content = base64.b64encode(svg_file.read()).decode('UTF-8')
                    svg_path = 'base64:{}'.format(svg_content)
                else:
                    svg_path = context.convert_path(svg_path)
            else:
                svg = PictureUtils.to_embedded_svg(picture.content,
                                                   ColorConverter.color_to_qcolor(layer.color_foreground),
                                                   ColorConverter.color_to_qcolor(layer.color_background),
                                                   ColorConverter.color_to_qcolor(layer.color_transparent))
                if context.embed_pictures:
                    svg_base64 = base64.b64encode(svg.encode('UTF-8')).decode('UTF-8')
                    svg_path = 'base64:{}'.format(svg_base64)
                else:
                    svg_path = SymbolConverter.write_svg(svg, context.symbol_name, context.get_picture_store_folder())
                    svg_path = context.convert_path(svg_path)

            out = QgsSvgMarkerSymbolLayer(svg_path, context.convert_size(layer.size), layer.angle)

            # esri symbol sizes are for height, QGIS are for width
            if out.defaultAspectRatio() != 1 and out.defaultAspectRatio() != 0:
                out.setSize(context.convert_size(layer.size) / out.defaultAspectRatio())

        else:
            if context.embed_pictures:
                picture_data = SymbolConverter.get_picture_data(picture, layer.color_foreground, layer.color_background,
                                                                layer.color_transparent,
                                                                context=context)
                image_base64 = base64.b64encode(picture_data).decode('UTF-8')
                image_path = 'base64:{}'.format(image_base64)
            else:
                image_path = SymbolConverter.write_picture(picture, context.symbol_name,
                                                           context.get_picture_store_folder(),
                                                           layer.color_foreground,
                                                           layer.color_background,
                                                           layer.color_transparent, context=context)
            # unsure -- should this angle be converted? probably!
            out = QgsRasterMarkerSymbolLayer(image_path, context.convert_size(layer.size), layer.angle)

        out.setSizeUnit(context.units)
        out.setEnabled(layer.enabled)
        out.setLocked(layer.locked)
        if layer.symbol_level != 0xffffffff:
            out.setRenderingPass(layer.symbol_level)
        out.setOffset(
            ConversionUtils.adjust_offset_for_rotation(
                QPointF(context.convert_size(layer.x_offset), -context.convert_size(layer.y_offset)),
                layer.angle))
        out.setOffsetUnit(context.units)

        symbol.appendSymbolLayer(out)
