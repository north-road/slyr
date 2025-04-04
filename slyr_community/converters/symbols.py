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
import uuid
from enum import Enum
from typing import (
    Union,
    Tuple
)

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
                       QgsRasterFillSymbolLayer,
                       QgsGradientFillSymbolLayer,
                       QgsGradientStop,
                       QgsShapeburstFillSymbolLayer,
                       QgsCentroidFillSymbolLayer,
                       QgsPointPatternFillSymbolLayer,
                       QgsSymbol
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
from qgis.PyQt.QtXml import QDomDocument

from ..parser.objects.multi_layer_symbols import (
    MultiLayerSymbol,
    MultiLayerFillSymbol,
    MultiLayerLineSymbol,
    MultiLayerMarkerSymbol
)
from ..parser.objects.symbol_layer import SymbolLayer
from ..parser.objects.line_symbol_layer import (
    SimpleLineSymbol,
    CartographicLineSymbol,
    MarkerLineSymbol,
    HashLineSymbol,
    LineSymbolLayer)
from ..parser.objects.fill_symbol_layer import (
    FillSymbolLayer,
    SimpleFillSymbol,
    ColorSymbol,
    LineFillSymbol,
    MarkerFillSymbol,
    PictureFillSymbol,
    GradientFillSymbol
)
from ..parser.objects.marker_symbol_layer import (
    MarkerSymbolLayer,
    SimpleMarkerSymbol,
    ArrowMarkerSymbol,
    CharacterMarkerSymbol,
    PictureMarkerSymbol
)
from ..parser.objects.dot_density_fill_symbol import DotDensityFillSymbol
from ..parser.objects.text_symbol import TextSymbol
from ..parser.objects.label_style import LabelStyle
from ..parser.objects.maplex_label_style import MaplexLabelStyle
from ..parser.exceptions import NotImplementedException
from .context import Context
from .color import ColorConverter
from .decorations import DecorationConverter
from ..parser.objects.simple_line3d_symbol import SimpleLine3DSymbol
from ..parser.objects.marker3d_symbol import Marker3DSymbol
from ..parser.objects.simple_marker3d_symbol import SimpleMarker3DSymbol
from ..parser.objects.character_marker3d_symbol import CharacterMarker3DSymbol
from ..parser.objects.texture_fill_symbol import TextureFillSymbol
from ..parser.objects.color_ramp_symbol import ColorRampSymbol
from ..parser.objects.ramps import ColorRamp

from .text_format import TextSymbolConverter
from .labels import LabelConverter
from .color_ramp import ColorRampConverter
from .utils import ConversionUtils
from .pictures import PictureUtils
from ..parser.objects.picture import (
    EmfPicture,
    StdPicture,
    BmpPicture
)
from ..bintools.file_utils import FileUtils


class SymbolConverter:  # pylint: disable=too-many-public-methods
    """
    Converts ArcObjects symbols to QGIS symbols
    """

    @staticmethod
    def null_symbol(symbol_type):
        """
        Returns a "null" symbol of the desired type
        """
        if symbol_type == QgsSymbol.Line:
            out = QgsLineSymbol()
            layer = QgsSimpleLineSymbolLayer(penStyle=Qt.NoPen)
            out.changeSymbolLayer(0, layer)
        else:
            assert False
        return out

    # pylint: disable=too-many-return-statements, too-many-branches, too-many-statements
    @staticmethod
    def Symbol_to_QgsSymbol(symbol, context: Context):
        """
        Converts a raw Symbol to a QgsSymbol
        """
        old_symbol_layer_output_to_input_index_map = context.symbol_layer_output_to_input_index_map
        old_current_symbol_layer = context.current_symbol_layer

        context.symbol_layer_output_to_input_index_map = {}

        if False:  # pylint: disable=using-constant-test
            pass

        if False and not symbol.layers:  # pylint: disable=condition-evals-to-constant
            return None

        if issubclass(symbol.__class__, (
        MultiLayerFillSymbol, FillSymbolLayer, TextureFillSymbol,)):
            out = QgsFillSymbol()
        elif False:  # pylint: disable=using-constant-test
            pass
        elif issubclass(symbol.__class__, (
        MultiLayerLineSymbol, LineSymbolLayer, SimpleLine3DSymbol,)):
            out = QgsLineSymbol()
        elif issubclass(symbol.__class__, (
                MultiLayerMarkerSymbol, MarkerSymbolLayer, Marker3DSymbol,
                SimpleMarker3DSymbol,
                CharacterMarker3DSymbol,)):
            if isinstance(symbol, MultiLayerMarkerSymbol) and symbol.halo:
                context.push_warning(
                    'Marker halos are not supported by QGIS')
            out = QgsMarkerSymbol()
        elif issubclass(symbol.__class__, ColorRamp):
            out = ColorRampConverter.ColorRamp_to_QgsColorRamp(symbol)
            context.final_symbol_layer_output_to_input_index_map = context.symbol_layer_output_to_input_index_map
            context.symbol_layer_output_to_input_index_map = old_symbol_layer_output_to_input_index_map
            context.current_symbol_layer = old_current_symbol_layer
            return out
        elif issubclass(symbol.__class__, ColorRampSymbol):
            out = QgsFillSymbol()
            SymbolConverter.append_GradientFillSymbolLayer(out, symbol,
                                                           context)
            out.deleteSymbolLayer(0)
            context.final_symbol_layer_output_to_input_index_map = context.symbol_layer_output_to_input_index_map
            context.symbol_layer_output_to_input_index_map = old_symbol_layer_output_to_input_index_map
            context.current_symbol_layer = old_current_symbol_layer
            return out
        elif issubclass(symbol.__class__, DotDensityFillSymbol):
            out = QgsFillSymbol()
            SymbolConverter.append_DotDensityFillSymbolLayer(out, symbol,
                                                             context)
            out.deleteSymbolLayer(0)
            context.final_symbol_layer_output_to_input_index_map = context.symbol_layer_output_to_input_index_map
            context.symbol_layer_output_to_input_index_map = old_symbol_layer_output_to_input_index_map
            context.current_symbol_layer = old_current_symbol_layer
            return out
        elif issubclass(symbol.__class__, (TextSymbol,)):
            context.final_symbol_layer_output_to_input_index_map = context.symbol_layer_output_to_input_index_map
            context.symbol_layer_output_to_input_index_map = old_symbol_layer_output_to_input_index_map
            context.current_symbol_layer = old_current_symbol_layer
            return TextSymbolConverter.text_symbol_to_qgstextformat(symbol,
                                                                    context)
        elif issubclass(symbol.__class__, LabelStyle) or issubclass(
                symbol.__class__, MaplexLabelStyle):
            context.final_symbol_layer_output_to_input_index_map = context.symbol_layer_output_to_input_index_map
            context.symbol_layer_output_to_input_index_map = old_symbol_layer_output_to_input_index_map
            context.current_symbol_layer = old_current_symbol_layer
            return LabelConverter.convert_label_style(symbol, context)
        else:
            context.final_symbol_layer_output_to_input_index_map = context.symbol_layer_output_to_input_index_map
            context.symbol_layer_output_to_input_index_map = old_symbol_layer_output_to_input_index_map
            context.current_symbol_layer = old_current_symbol_layer

            raise NotImplementedException(
                '{} symbols cannot be converted yet'.format(
                    symbol.__class__.__name__),
                symbol)

        context.current_symbol = symbol
        context.current_symbol_layer = None
        SymbolConverter.add_symbol_layers(out, symbol, context)

        context.final_symbol_layer_output_to_input_index_map = context.symbol_layer_output_to_input_index_map
        context.symbol_layer_output_to_input_index_map = old_symbol_layer_output_to_input_index_map
        context.current_symbol_layer = old_current_symbol_layer

        return out

    # pylint: enable=too-many-return-statements, too-many-branches, too-many-statements

    @staticmethod
    def symbol_to_color(symbol, context: Context):
        """
        Converts an ESRI symbol to a single color best representing the symbol
        """
        s = SymbolConverter.Symbol_to_QgsSymbol(symbol, context)
        if issubclass(symbol.__class__, MultiLayerFillSymbol):
            all_null = True
            for layer in symbol.layers:
                if isinstance(layer, SimpleFillSymbol) and symbol.layers[
                    0].fill_style == SimpleFillSymbol.STYLE_NULL:
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
        elif s is None:
            c = QColor(0, 0, 0)
            c.setAlpha(0)
            return c

        return s.color()

    @staticmethod
    def symbol_to_line_color(symbol, context: Context):
        """
        Converts an ESRI symbol to a single color best representing the symbol's line color
        """
        s = SymbolConverter.Symbol_to_QgsSymbol(symbol, context)
        if isinstance(s, QgsFillSymbol):
            for i in range(s.symbolLayerCount()):
                layer = s.symbolLayer(i)
                if isinstance(layer,
                              QgsSimpleFillSymbolLayer) and not layer.strokeStyle() == Qt.NoPen:
                    return layer.strokeColor()
                elif isinstance(layer, QgsSimpleLineSymbolLayer):
                    return layer.color()
            return None
        else:
            return s.color()

    @staticmethod
    def symbol_to_line_width(symbol, context: Context) -> float:
        """
        Converts an ESRI symbol to a single line width value best representing the symbol
        """
        s = SymbolConverter.Symbol_to_QgsSymbol(symbol, context)
        if isinstance(s, QgsFillSymbol):
            for i in range(s.symbolLayerCount()):
                layer = s.symbolLayer(i)
                if isinstance(layer,
                              QgsSimpleFillSymbolLayer) and not layer.strokeStyle() == Qt.NoPen:
                    return layer.strokeWidth()
                elif isinstance(layer, QgsSimpleLineSymbolLayer):
                    return layer.width()
            return None
        else:
            return s.width()

    @staticmethod
    def symbol_to_marker_size(symbol, context: Context) -> float:
        """
        Converts an ESRI symbol to a single marker size value best representing the symbol
        """
        s = SymbolConverter.Symbol_to_QgsSymbol(symbol, context)
        return s.size()

    @staticmethod
    def symbol_to_marker_shape(symbol,
                               context: Context) -> str:  # pylint: disable=unused-argument
        """
        Converts an ESRI symbol to a marker shape string ("circle" or "square") best representing the symbol
        """
        if isinstance(symbol, SimpleMarkerSymbol):
            return symbol.type

        elif isinstance(symbol, MultiLayerMarkerSymbol) and len(
                symbol.layers) == 1 and isinstance(symbol.layers[0],
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
            context.current_symbol_layer = 0
            SymbolConverter.append_SymbolLayer_to_QgsSymbolLayer(out, symbol,
                                                                 context)
        else:
            layers = symbol.layers
            prev_use_real_world_symbol_sizes = context.use_real_world_units
            if False:  # pylint: disable=using-constant-test
                pass

            for idx, layer in enumerate(layers):
                context.current_symbol_layer = idx
                SymbolConverter.append_SymbolLayer_to_QgsSymbolLayer(out,
                                                                     layer,
                                                                     context)
                if False:  # pylint: disable=using-constant-test
                    pass

            if True and symbol.symbol_level != 0xffffffff:  # pylint: disable=simplifiable-condition
                # 0xffffffff = sub layers have own level
                for i in range(out.symbolLayerCount()):
                    out.symbolLayer(i).setRenderingPass(symbol.symbol_level)

            context.use_real_world_units = prev_use_real_world_symbol_sizes
            context.global_cim_effects = []

        if out.symbolLayerCount() == 0:
            # we appended nothing! Add a dummy invisible layer to avoid QGIS adding a default layer to this
            if isinstance(out, QgsMarkerSymbol):
                layer = QgsSimpleMarkerSymbolLayer(color=QColor(0, 0, 0, 0))
                layer.setStrokeStyle(Qt.NoPen)
                out.appendSymbolLayer(layer)
                context.symbol_layer_output_to_input_index_map[
                    layer] = context.current_symbol_layer
            elif isinstance(out, QgsLineSymbol):
                layer = QgsSimpleLineSymbolLayer(color=QColor(0, 0, 0, 0),
                                                 penStyle=Qt.NoPen)
                out.appendSymbolLayer(layer)
                context.symbol_layer_output_to_input_index_map[
                    layer] = context.current_symbol_layer
            elif isinstance(out, QgsFillSymbol):
                layer = QgsSimpleFillSymbolLayer(color=QColor(0, 0, 0, 0),
                                                 style=Qt.NoBrush,
                                                 strokeStyle=Qt.NoPen)
                out.appendSymbolLayer(layer)
                context.symbol_layer_output_to_input_index_map[
                    layer] = context.current_symbol_layer

        context.current_symbol_layer = None
        return out

    @staticmethod
    def append_SymbolLayer_to_QgsSymbolLayer(symbol,
                                             # pylint: disable=too-many-statements,too-many-branches
                                             layer,
                                             context: Context):
        """
        Appends a SymbolLayer to a QgsSymbolLayer
        """
        if issubclass(layer.__class__, (SymbolLayer, )):
            if issubclass(layer.__class__,
                          (FillSymbolLayer, )):
                SymbolConverter.append_FillSymbolLayer(symbol, layer, context)
            elif issubclass(layer.__class__,
                            (LineSymbolLayer, )):
                SymbolConverter.append_LineSymbolLayer(symbol, layer, context)
            elif issubclass(layer.__class__,
                            (MarkerSymbolLayer, )):
                SymbolConverter.append_MarkerSymbolLayer(symbol, layer,
                                                         context)
            elif issubclass(layer.__class__, Marker3DSymbol):
                SymbolConverter.append_Marker3DSymbolLayer(symbol, layer,
                                                           context)
            elif issubclass(layer.__class__, SimpleMarker3DSymbol):
                SymbolConverter.append_SimpleMarker3DSymbolLayer(symbol, layer,
                                                                 context)
            elif issubclass(layer.__class__, SimpleLine3DSymbol):
                SymbolConverter.append_SimpleLine3DSymbolLayer(symbol, layer,
                                                               context)
            elif issubclass(layer.__class__, CharacterMarker3DSymbol):
                SymbolConverter.append_CharacterMarker3DSymbolLayer(symbol,
                                                                    layer,
                                                                    context)
            elif issubclass(layer.__class__, TextureFillSymbol):
                SymbolConverter.append_TextureFillSymbolLayer(symbol, layer,
                                                              context)
            elif issubclass(layer.__class__, ColorRampSymbol):
                SymbolConverter.append_FillSymbolLayer(symbol, layer, context)
            else:
                raise NotImplementedException(
                    'Converting {} not implemented yet'.format(
                        layer.__class__.__name__))
        else:
            for sublayer in layer.layers:
                SymbolConverter.append_SymbolLayer_to_QgsSymbolLayer(symbol,
                                                                     sublayer,
                                                                     context)

    @staticmethod
    def append_FillSymbolLayer(symbol, layer, context: Context):
        """
        Appends a FillSymbolLayer to a symbol
        """
        if isinstance(layer, (SimpleFillSymbol, ColorSymbol)):
            SymbolConverter.append_SimpleFillSymbolLayer(symbol, layer,
                                                         context)
        elif False:  # pylint: disable=using-constant-test
            pass
        elif isinstance(layer, (LineFillSymbol, )):
            SymbolConverter.append_LineFillSymbolLayer(symbol, layer, context)
        elif isinstance(layer, MarkerFillSymbol):
            SymbolConverter.append_MarkerFillSymbolLayer(symbol, layer,
                                                         context)
        elif isinstance(layer, PictureFillSymbol):
            SymbolConverter.append_PictureFillSymbolLayer(symbol, layer,
                                                          context)
        elif isinstance(layer, DotDensityFillSymbol):
            SymbolConverter.append_DotDensityFillSymbolLayer(symbol, layer,
                                                             context)
        elif False:  # pylint: disable=using-constant-test
            pass
        elif isinstance(layer, (GradientFillSymbol, )):
            SymbolConverter.append_GradientFillSymbolLayer(symbol, layer,
                                                           context)
        else:
            raise NotImplementedException(
                'Converting {} not implemented yet'.format(
                    layer.__class__.__name__))

    @staticmethod
    def append_LineSymbolLayer(symbol, layer, context: Context):
        """
        Appends a LineSymbolLayer to a QgsSymbol
        """
        if isinstance(layer, (SimpleLineSymbol, )):
            SymbolConverter.append_SimpleLineSymbolLayer(symbol, layer,
                                                         context)
        elif False:  # pylint: disable=using-constant-test
            pass
        elif isinstance(layer, CartographicLineSymbol):
            SymbolConverter.append_CartographicLineSymbolLayer(symbol, layer,
                                                               context)
        elif isinstance(layer, (MarkerLineSymbol, HashLineSymbol)):
            SymbolConverter.append_TemplatedLineSymbolLayer(symbol, layer,
                                                            context)
        elif False:  # pylint: disable=using-constant-test
            pass
        elif False:  # pylint: disable=using-constant-test
            pass
        else:
            raise NotImplementedException(
                'Converting {} not implemented yet'.format(
                    layer.__class__.__name__))

    @staticmethod
    def append_MarkerSymbolLayer(symbol, layer, context: Context):
        """
        Appends a MarkerSymbolLayer to a QgsSymbol
        """
        if isinstance(layer, SimpleMarkerSymbol):
            SymbolConverter.append_SimpleMarkerSymbolLayer(symbol, layer,
                                                           context)
        elif False:  # pylint: disable=using-constant-test
            pass
        elif False:  # pylint: disable=using-constant-test
            pass
        elif isinstance(layer, ArrowMarkerSymbol):
            SymbolConverter.append_ArrowMarkerSymbolLayer(symbol, layer,
                                                          context)
        elif isinstance(layer, (CharacterMarkerSymbol, )):
            SymbolConverter.append_CharacterMarkerSymbolLayer(symbol, layer,
                                                              context)
        elif isinstance(layer, PictureMarkerSymbol):
            SymbolConverter.append_PictureMarkerSymbolLayer(symbol, layer,
                                                            context)
        elif False:  # pylint: disable=using-constant-test
            pass
        else:
            raise NotImplementedException(
                'Converting {} not implemented yet'.format(
                    layer.__class__.__name__))

    @staticmethod
    def append_SimpleFillSymbolLayer(symbol,
                                     # pylint: disable=too-many-branches,too-many-statements
                                     layer: SimpleFillSymbol,
                                     context: Context):
        """
        Appends a SimpleFillSymbolLayer to a symbol
        """
        fill_color = ColorConverter.color_to_qcolor(layer.color)
        out = QgsSimpleFillSymbolLayer(fill_color)
        out.setEnabled(layer.enabled)
        out.setLocked(layer.locked)
        if True and layer.symbol_level != 0xffffffff:  # pylint: disable=simplifiable-condition
            out.setRenderingPass(layer.symbol_level)

        if isinstance(layer, SimpleFillSymbol):
            if layer.outline and not isinstance(layer.outline,
                                                MultiLayerLineSymbol):
                # these properties are not supported in QGIS simple fill, so we need
                # to add an additional outline layer to support them
                uses_complex_outline = \
                    (hasattr(layer.outline,
                             'offset') and layer.outline.offset) or \
                    (hasattr(layer.outline, 'template') and
                        layer.outline.template and
                        len(
                                layer.outline.template.pattern_parts) > 0) or \
                    (hasattr(layer.outline, 'decoration') and
                        layer.outline.decoration)
                if not uses_complex_outline:
                    # great, we can avoid the extra symbol layer!
                    if isinstance(layer.outline,
                                  (SimpleLineSymbol, CartographicLineSymbol)):
                        out.setStrokeColor(ColorConverter.color_to_qcolor(
                            layer.outline.color))
                        out.setStrokeWidth(context.convert_size(
                            context.fix_line_width(layer.outline.width)))
                        out.setStrokeWidthUnit(context.units)
                    if isinstance(layer.outline, SimpleLineSymbol):
                        out.setStrokeStyle(
                            ConversionUtils.symbol_pen_to_qpenstyle(
                                layer.outline.line_type) if layer.outline.width > 0 else Qt.NoPen)
                    if isinstance(layer.outline, CartographicLineSymbol):
                        out.setPenJoinStyle(
                            ConversionUtils.symbol_pen_to_qpenjoinstyle(
                                layer.outline.join))
                        if layer.outline.width <= 0:
                            out.setStrokeStyle(Qt.NoPen)
                    # better matching of null stroke color to QGIS symbology
                    if out.strokeColor().alpha() == 0:
                        out.setStrokeStyle(Qt.NoPen)

                    if context.apply_conversion_tweaks and \
                            (
                                    out.strokeColor().alpha() == 0 or out.strokeStyle() == Qt.NoPen) and \
                            (out.color().alpha() == 0):
                        # skip empty layers
                        return

                    symbol.appendSymbolLayer(out)
                else:
                    out.setStrokeStyle(Qt.NoPen)

                    if not context.apply_conversion_tweaks or out.color().alpha() != 0:
                        symbol.appendSymbolLayer(out)

                    SymbolConverter.append_SymbolLayer_to_QgsSymbolLayer(
                        symbol, layer.outline, context)
            elif isinstance(layer.outline, MultiLayerLineSymbol):
                # outline is a symbol itself
                out.setStrokeStyle(Qt.NoPen)

                if not context.apply_conversion_tweaks or out.color().alpha() != 0:
                    symbol.appendSymbolLayer(out)

                # get all layers from outline
                SymbolConverter.append_SymbolLayer_to_QgsSymbolLayer(symbol,
                                                                     layer.outline,
                                                                     context)
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

        elif isinstance(layer, (ColorSymbol, )):
            out.setStrokeStyle(Qt.NoPen)

            if False:  # pylint: disable=using-constant-test
                pass
            else:
                if not context.apply_conversion_tweaks or out.color().alpha() != 0:
                    symbol.appendSymbolLayer(out)
                    context.symbol_layer_output_to_input_index_map[
                        out] = context.current_symbol_layer

    @staticmethod
    def append_LineFillSymbolLayer(symbol,
                                   layer: LineFillSymbol,
                                   context: Context):
        """
        Appends a LineFillSymbolLayer to a symbol
        """
        line = SymbolConverter.Symbol_to_QgsSymbol(layer.line, context)

        out = QgsLinePatternFillSymbolLayer()
        out.setEnabled(layer.enabled)
        out.setLocked(layer.locked)
        if True and layer.symbol_level != 0xffffffff:  # pylint: disable=simplifiable-condition
            out.setRenderingPass(layer.symbol_level)
        out.setSubSymbol(line)
        out.setLineAngle(layer.angle or 0)

        separation = layer.separation
        # if context.apply_conversion_tweaks:
        #    min_separation = 5 * max(line.width(),
        #                             0.5 if line.symbolLayer(0).widthUnit() == QgsUnitTypes.RenderPoints else 0.18)
        #    separation = max(min_separation, separation)
        #    if context.units == QgsUnitTypes.RenderMillimeters:
        #        separation *= 0.352

        if True:  # pylint: disable=using-constant-test
            out.setDistance(context.convert_size(separation))
            out.setDistanceUnit(context.units)
        else:
            pass

        if True:  # pylint: disable=using-constant-test
            out.setOffset(context.convert_size(layer.offset))
            out.setOffsetUnit(context.units)
        else:
            pass

        if False:  # pylint: disable=using-constant-test
            pass
        else:
            symbol.appendSymbolLayer(out)
            context.symbol_layer_output_to_input_index_map[
                out] = context.current_symbol_layer

        if True:  # pylint: disable=using-constant-test
            if isinstance(layer.outline, MultiLayerLineSymbol):
                # get all layers from outline
                SymbolConverter.append_SymbolLayer_to_QgsSymbolLayer(symbol,
                                                                     layer.outline,
                                                                     context)
            elif layer.outline:
                SymbolConverter.append_SymbolLayer_to_QgsSymbolLayer(symbol,
                                                                     layer.outline,
                                                                     context)

    # pylint: disable=too-many-statements,too-many-branches
    @staticmethod
    def append_GradientFillSymbolLayer(
            symbol,
            layer: Union[GradientFillSymbol, ColorRampSymbol, ],
            context: Context):
        """
        Appends a append_GradientFillSymbolLayer to a symbol
        """
        if isinstance(layer, ColorRampSymbol):
            ramp = ColorRampConverter.ColorRamp_to_QgsColorRamp(
                layer.color_ramp)
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
                    stops = [QgsGradientStop(1 - percent,
                                             ramp.color1())] + stops
                    ramp.setStops(stops)

        # pylint: disable=simplifiable-condition
        if (isinstance(layer, GradientFillSymbol) and
            layer.type in (
            GradientFillSymbol.RECTANGULAR, GradientFillSymbol.BUFFERED)) or \
                False:
            if (
                    (isinstance(layer,
                                GradientFillSymbol) and layer.type == GradientFillSymbol.RECTANGULAR) or
                    False):
                # pylint: enable=simplifiable-condition
                context.push_warning(
                    'Rectangular gradients are not supported in QGIS, '
                    'using buffered gradient instead'
                )

            if Qgis.QGIS_VERSION_INT < 30900:
                # can cause crash in < 3.10
                if context.unsupported_object_callback:
                    context.push_warning(
                        'Buffered gradients are not supported in QGIS < 3.10'
                    )
                    return
                else:
                    raise NotImplementedException(
                        'Buffered gradients are not supported in QGIS < 3.10')
            out = QgsShapeburstFillSymbolLayer()
            out.setColorType(QgsShapeburstFillSymbolLayer.ColorRamp)
            ramp.invert()
            if True:  # pylint: disable=using-constant-test
                scale_ramp(ramp, layer.percent)
            else:
                pass
            ramp.invert()
            out.setColorRamp(ramp)

            if False:  # pylint: disable=using-constant-test
                pass

            out.setEnabled(layer.enabled)
            out.setLocked(layer.locked)
            if True and layer.symbol_level != 0xffffffff:  # pylint: disable=simplifiable-condition
                out.setRenderingPass(layer.symbol_level)

            if False:  # pylint: disable=using-constant-test
                pass
            else:
                symbol.appendSymbolLayer(out)
                context.symbol_layer_output_to_input_index_map[
                    out] = context.current_symbol_layer
            return
        elif isinstance(layer,
                        GradientFillSymbol) and layer.type == GradientFillSymbol.CIRCULAR:
            ref_1 = QPointF(0.5, 0.5)
            ref_2 = QPointF(1.0, 0.5)
            gradient_type = QgsGradientFillSymbolLayer.Radial
            # yep!!
            ramp.invert()
            scale_ramp(ramp, layer.percent)
        elif False:  # pylint: disable=using-constant-test
            pass
        # pylint: disable=simplifiable-condition
        elif isinstance(layer, ColorRampSymbol) or (
                isinstance(layer,
                           GradientFillSymbol) and layer.type == GradientFillSymbol.LINEAR) or \
                False:
            # pylint: enable=simplifiable-condition
            l1 = QLineF(0.5, 0.5, 1, 0.5)
            l2 = QLineF(0.5, 0.5, 0, 0.5)

            if isinstance(layer, ColorRampSymbol):
                angle = 0 if layer.horizontal else 270
                percent = 100
            else:
                if isinstance(layer, GradientFillSymbol):
                    percent = layer.percent
                else:
                    pass

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

        out = QgsGradientFillSymbolLayer(
            gradientColorType=QgsGradientFillSymbolLayer.ColorRamp,
            gradientType=gradient_type)
        out.setColorRamp(ramp)
        out.setReferencePoint1(ref_1)
        out.setReferencePoint2(ref_2)
        if isinstance(layer, (GradientFillSymbol, )):
            out.setEnabled(layer.enabled)
            out.setLocked(layer.locked)
            if isinstance(layer,
                          GradientFillSymbol) and layer.symbol_level != 0xffffffff:
                out.setRenderingPass(layer.symbol_level)

        if False:  # pylint: disable=using-constant-test
            pass
        else:
            symbol.appendSymbolLayer(out)
            context.symbol_layer_output_to_input_index_map[
                out] = context.current_symbol_layer

    # pylint: enable=too-many-statements,too-many-branches

    @staticmethod
    def append_MarkerFillSymbolLayer(symbol, layer: MarkerFillSymbol,
                                     context: Context):
        """
        Appends a MarkerFillSymbolLayer to a symbol
        """
        if layer.random and Qgis.QGIS_VERSION_INT < 31100:
            context.push_warning(
                'Random marker fills are only supported on QGIS 3.12 or later'
            )

        if Qgis.QGIS_VERSION_INT < 30700:
            if layer.offset_x or layer.offset_y:
                context.push_warning(
                    'Marker fill offset X or Y is only supported on '
                    'QGIS 3.8 or later'
                )

        marker = SymbolConverter.Symbol_to_QgsSymbol(layer.marker, context)

        if layer.random and Qgis.QGIS_VERSION_INT >= 31100:
            from qgis.core import \
                QgsRandomMarkerFillSymbolLayer  # pylint: disable=import-outside-toplevel

            density = layer.separation_x * layer.separation_y / 10
            out = QgsRandomMarkerFillSymbolLayer(1,
                                                 QgsRandomMarkerFillSymbolLayer.DensityBasedCount,
                                                 density)
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
        context.symbol_layer_output_to_input_index_map[
            out] = context.current_symbol_layer

        if isinstance(layer.outline, MultiLayerLineSymbol):
            # get all layers from outline
            SymbolConverter.append_SymbolLayer_to_QgsSymbolLayer(symbol,
                                                                 layer.outline,
                                                                 context)
        elif layer.outline:
            SymbolConverter.append_SymbolLayer_to_QgsSymbolLayer(symbol,
                                                                 layer.outline,
                                                                 context)

    @staticmethod
    def append_DotDensityFillSymbolLayer(symbol, layer: DotDensityFillSymbol,
                                         context: Context):
        """
        Appends a DotDensityFillSymbol to a symbol
        """
        if Qgis.QGIS_VERSION_INT < 31100 and context.unsupported_object_callback:
            raise NotImplementedException(
                '{}: Dot density fills are only supported on QGIS 3.12 or later'.format(
                    context.layer_name or context.symbol_name))

        if len(layer.markers) > 1:
            raise NotImplementedException(
                '{}: Dot density fills with multiple markers are not currently support'.format(
                    context.layer_name or context.symbol_name))

        marker = SymbolConverter.Symbol_to_QgsSymbol(layer.markers[0], context)

        from qgis.core import \
            QgsRandomMarkerFillSymbolLayer  # pylint: disable=import-outside-toplevel

        out = QgsRandomMarkerFillSymbolLayer(layer.dot_counts[0],
                                             QgsRandomMarkerFillSymbolLayer.AbsoluteCount)
        out.setClipPoints(layer.use_mask)
        out.setSeed(layer.seed)

        out.setSubSymbol(marker)
        out.setEnabled(True)
        out.setLocked(False)

        symbol.appendSymbolLayer(out)
        context.symbol_layer_output_to_input_index_map[
            out] = context.current_symbol_layer

        if isinstance(layer.outline_symbol, MultiLayerLineSymbol):
            # get all layers from outline
            SymbolConverter.append_SymbolLayer_to_QgsSymbolLayer(symbol,
                                                                 layer.outline_symbol,
                                                                 context)
        elif layer.outline_symbol:
            SymbolConverter.append_SymbolLayer_to_QgsSymbolLayer(symbol,
                                                                 layer.outline_symbol,
                                                                 context)

    @staticmethod
    def symbol_name_to_filename(symbol_name: str, picture_folder: str,
                                extension: str) -> str:
        """
        Returns a new unique filename for the given symbol to use
        """
        safe_symbol_name = FileUtils.clean_symbol_name_for_file(symbol_name)

        if not safe_symbol_name:
            safe_symbol_name = str(uuid.uuid4())

        path = os.path.join(picture_folder, safe_symbol_name + '.' + extension)
        counter = 1
        while os.path.exists(path):
            path = os.path.join(picture_folder, safe_symbol_name + '_' + str(
                counter) + '.' + extension)
            counter += 1

        return path

    # pylint: disable=too-many-branches, too-many-statements
    @staticmethod
    def emf_to_svg(emf_path: str, svg_path: str, inkscape_path: str = None,
                   context: Context = None):
        """
        Converts an EMF file to an SVG file (using inkscape)
        """
        binary = 'inkscape'
        if inkscape_path is not None:
            binary = inkscape_path
        likely_invalid_path = False

        # most recent inkscape version arguments
        export_args = [binary,
                       '--export-plain-svg',
                       '--export-area-drawing',
                       '-o',
                       svg_path,
                       emf_path
                       ]

        CREATE_NO_WINDOW = 0x08000000
        # pylint: disable=subprocess-run-check
        try:
            try:
                _ = subprocess.run(export_args,
                                   stdout=subprocess.PIPE,
                                   creationflags=CREATE_NO_WINDOW)
            except ValueError:
                _ = subprocess.run(export_args,
                                   stdout=subprocess.PIPE)
        except FileNotFoundError:
            pass
        except PermissionError:
            likely_invalid_path = True

        if not os.path.exists(svg_path):
            # bah, inkscape changed parameters!
            export_args = [binary,
                           '--export-plain-svg',
                           '--export-file',
                           svg_path,
                           emf_path
                           ]

            try:
                try:
                    _ = subprocess.run(export_args,
                                       stdout=subprocess.PIPE,
                                       creationflags=CREATE_NO_WINDOW)
                except ValueError:
                    _ = subprocess.run(export_args,
                                       stdout=subprocess.PIPE)
            except FileNotFoundError:
                pass
            except PermissionError:
                likely_invalid_path = True

        if not os.path.exists(svg_path):
            # this is the command for a very old inkscape version (pre 1.0)
            export_args = [binary,
                           '--file',
                           emf_path,
                           '--export-plain-svg',
                           svg_path]

            try:
                try:
                    _ = subprocess.run(export_args,
                                       stdout=subprocess.PIPE,
                                       creationflags=CREATE_NO_WINDOW)
                except ValueError:
                    _ = subprocess.run(export_args,
                                       stdout=subprocess.PIPE)
            except FileNotFoundError:
                pass
            except PermissionError:
                likely_invalid_path = True

        # pylint: enable=subprocess-run-check
        if not os.path.exists(svg_path):
            # didn't work
            if likely_invalid_path:
                context.push_warning(
                    'Invalid path to Inkscape executable -- cannot convert EMF content',
                    level=Context.CRITICAL)
            else:
                context.push_warning(
                    'Conversion of EMF content requires a valid path to an Inkscape install setup in the SLYR options',
                    level=Context.CRITICAL)

        else:
            # remove width/height from svg tag, so that the viewbox is correctly re-calculated
            with open(svg_path, 'rt', encoding='utf-8') as svg_file:
                doc = QDomDocument()
                doc.setContent(''.join(svg_file.readlines()))

                doc.documentElement().removeAttribute('width')
                doc.documentElement().removeAttribute('height')

                out = doc.toString(2)
            with open(svg_path, 'wt', encoding='utf-8') as svg_file:
                svg_file.write(out)

    # pylint: enable=too-many-branches, too-many-statements

    @staticmethod
    def write_svg(content: str, symbol_name: str, picture_folder: str):
        """
        Writes a picture binary content to an SVG file
        """
        path = SymbolConverter.symbol_name_to_filename(symbol_name,
                                                       picture_folder, 'svg')
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
        trans_color = ColorConverter.color_to_qcolor(
            trans) if trans and not trans.is_null else None
        if picture is None or picture.content is None:
            if context and context.unsupported_object_callback:
                context.unsupported_object_callback(
                    '{}: Picture data is missing or corrupt'.format(
                        context.layer_name or context.symbol_name),
                    level=Context.CRITICAL)
            return None
        else:
            return PictureUtils.set_colors(picture.content, fg_color, bg_color,
                                           trans_color)

    @staticmethod
    def write_picture(picture, symbol_name: str, picture_folder: str, fg, bg,
                      trans, context=None):
        """
        Writes a picture binary content to a file, converting raster colors if necessary
        """
        new_content = SymbolConverter.get_picture_data(picture, fg, bg, trans,
                                                       context=context)

        path = SymbolConverter.symbol_name_to_filename(symbol_name,
                                                       picture_folder, 'png')
        PictureUtils.to_png(new_content, path)
        return path

    @staticmethod
    def append_PictureFillSymbolLayer(symbol,
                                      # pylint: disable=too-many-statements,too-many-branches,too-many-locals
                                      layer: PictureFillSymbol,
                                      context: Context):
        """
        Appends a PictureFillSymbolLayer to a symbol
        """
        if Qgis.QGIS_VERSION_INT < 30700:
            if layer.offset_x or layer.offset_y:
                context.push_warning(
                    'Marker fill offset X or Y is only '
                    'supported on QGIS 3.8 or later'
                )
        if (layer.separation_x or layer.separation_y):
            context.push_warning('Picture fill separation X or Y '
                                 'is not supported by QGIS'
                                 )

        picture = layer.picture
        if issubclass(picture.__class__, StdPicture):
            picture = picture.picture

        if issubclass(picture.__class__, EmfPicture):
            path = SymbolConverter.symbol_name_to_filename(context.symbol_name,
                                                           context.get_picture_store_folder(),
                                                           'emf')
            with open(path, 'wb') as f:
                f.write(picture.content)

            svg_path = SymbolConverter.symbol_name_to_filename(
                context.symbol_name, context.get_picture_store_folder(),
                'svg')
            SymbolConverter.emf_to_svg(path, svg_path,
                                       inkscape_path=context.inkscape_path,
                                       context=context)
            # no longer need the emf file
            try:
                os.remove(path)
            except PermissionError:
                pass

            if not os.path.exists(svg_path):
                context.push_warning(
                    'Conversion of EMF picture failed',
                    level=Context.CRITICAL)

            width_in_in_points = layer.scale_x * QSvgRenderer(
                svg_path).viewBoxF().width()

            if context.embed_pictures and os.path.exists(svg_path):
                with open(svg_path, 'rb') as svg_file:
                    svg_content = base64.b64encode(svg_file.read()).decode(
                        'UTF-8')
                # no longer need the svg file
                try:
                    os.remove(svg_path)
                except PermissionError:
                    pass
                svg_path = 'base64:{}'.format(svg_content)
            else:
                svg_path = context.convert_path(svg_path)

            out = QgsSVGFillSymbolLayer(svg_path, context.convert_size(
                width_in_in_points),
                                        ConversionUtils.convert_angle(
                                            layer.angle))
            out.setPatternWidthUnit(context.units)
            outline = QgsLineSymbol()
            outline.changeSymbolLayer(0, QgsSimpleLineSymbolLayer(
                penStyle=Qt.NoPen))
            out.setSubSymbol(outline)
        else:
            # use raster fill
            if context.embed_pictures and Qgis.QGIS_VERSION_INT >= 30600:
                picture_data = SymbolConverter.get_picture_data(picture,
                                                                layer.color_foreground,
                                                                layer.color_background,
                                                                None,
                                                                context=context)
                if picture_data:
                    image_base64 = base64.b64encode(picture_data).decode(
                        'UTF-8')
                    image_path = 'base64:{}'.format(image_base64)
                else:
                    image_path = ''
            else:
                image_path = SymbolConverter.write_picture(picture,
                                                           context.symbol_name,
                                                           context.get_picture_store_folder(),
                                                           layer.color_foreground,
                                                           layer.color_background,
                                                           None,
                                                           context=context)

            out = QgsRasterFillSymbolLayer(image_path)

            if picture and picture.content:
                # convert to points, so that print layouts work nicely. It's a better match for Arc anyway
                width_in_pixels = layer.scale_x * PictureUtils.width_pixels(
                    picture.content)
                width_in_in_points = width_in_pixels / 96 * 72

                out.setWidth(context.convert_size(width_in_in_points))
                out.setWidthUnit(context.units)

            out.setAngle(ConversionUtils.convert_angle(layer.angle))

        out.setEnabled(layer.enabled)
        out.setLocked(layer.locked)
        if layer.symbol_level != 0xffffffff:
            out.setRenderingPass(layer.symbol_level)
        symbol.appendSymbolLayer(out)
        context.symbol_layer_output_to_input_index_map[
            out] = context.current_symbol_layer
        if isinstance(layer.outline, MultiLayerLineSymbol):
            # get all layers from outline
            SymbolConverter.append_SymbolLayer_to_QgsSymbolLayer(symbol,
                                                                 layer.outline,
                                                                 context)
        elif layer.outline:
            SymbolConverter.append_SymbolLayer_to_QgsSymbolLayer(symbol,
                                                                 layer.outline,
                                                                 context)

    @staticmethod
    def append_TextureFillSymbolLayer(symbol, layer: TextureFillSymbol,
                                      context: Context):
        """
        Appends a TextureFillSymbol to a symbol
        """
        if not layer.texture:
            return

        picture = layer.texture.picture
        if not picture:
            return

        context.push_warning('3D texture fill was converted to a 2d fill')

        # use raster fill
        if context.embed_pictures and Qgis.QGIS_VERSION_INT >= 30600:
            picture_data = SymbolConverter.get_picture_data(picture, None,
                                                            layer.color,
                                                            layer.transparency_color,
                                                            context=context)
            image_base64 = base64.b64encode(picture_data).decode('UTF-8')
            image_path = 'base64:{}'.format(image_base64)
        else:
            image_path = SymbolConverter.write_picture(picture,
                                                       context.symbol_name,
                                                       context.get_picture_store_folder(),
                                                       None, layer.color,
                                                       layer.transparency_color,
                                                       context=context)

        out = QgsRasterFillSymbolLayer(image_path)

        # convert to points, so that print layouts work nicely. It's a better match for Arc anyway
        width_in_pixels = layer.size * PictureUtils.width_pixels(
            picture.content)
        width_in_in_points = width_in_pixels / 96 * 72 / 2.5

        out.setWidth(context.convert_size(width_in_in_points))
        out.setWidthUnit(context.units)

        out.setAngle(ConversionUtils.convert_angle(layer.angle))

        out.setEnabled(layer.enabled)
        out.setLocked(layer.locked)
        if layer.symbol_level != 0xffffffff:
            out.setRenderingPass(layer.symbol_level)
        symbol.appendSymbolLayer(out)
        context.symbol_layer_output_to_input_index_map[
            out] = context.current_symbol_layer
        if isinstance(layer.outline, MultiLayerLineSymbol):
            # get all layers from outline
            SymbolConverter.append_SymbolLayer_to_QgsSymbolLayer(symbol,
                                                                 layer.outline,
                                                                 context)
        elif layer.outline:
            SymbolConverter.append_SymbolLayer_to_QgsSymbolLayer(symbol,
                                                                 layer.outline,
                                                                 context)

    @staticmethod
    def append_SimpleLineSymbolLayer(symbol, layer, context: Context):
        """
        Appends a SimpleLineSymbolLayer to a symbol
        """

        color = ColorConverter.color_to_qcolor(layer.color)
        out = QgsSimpleLineSymbolLayer(color)
        out.setEnabled(layer.enabled)
        out.setLocked(layer.locked)
        if True and layer.symbol_level != 0xffffffff:  # pylint: disable=simplifiable-condition
            out.setRenderingPass(layer.symbol_level)

        if True:  # pylint: disable=using-constant-test
            out.setWidth(
                context.convert_size(context.fix_line_width(
                    layer.width)))  # sometimes lines have negative width?
            out.setWidthUnit(context.units)
        else:
            pass

        if True:  # pylint: disable=using-constant-test
            # for arcgis, a pen width of 0 is not drawn, yet in QGIS it's a "hairline" size
            out.setPenStyle(ConversionUtils.symbol_pen_to_qpenstyle(
                layer.line_type) if layer.width > 0 else Qt.NoPen)
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
            context.symbol_layer_output_to_input_index_map[
                out] = context.current_symbol_layer
        else:
            pass

    @staticmethod
    def circular_mean(angles):
        """
        Calculates average angle
        """
        x = y = 0.
        for angle in angles:
            x += math.cos(math.radians(angle))
            y += math.sin(math.radians(angle))

        mean = (math.degrees(math.atan2(y, x)) + 360) % 360
        return mean

    @staticmethod
    def append_SimpleLine3DSymbolLayer(symbol, layer: SimpleLine3DSymbol,
                                       context: Context):
        """
        Appends a SimpleLine3DSymbol to a symbol
        """
        context.push_warning('3D line was converted to a simple line')
        color = ColorConverter.color_to_qcolor(layer.color)
        out = QgsSimpleLineSymbolLayer(color)
        out.setEnabled(layer.enabled)
        out.setLocked(layer.locked)
        if layer.symbol_level != 0xffffffff:
            out.setRenderingPass(layer.symbol_level)
        out.setWidth(context.convert_size(context.fix_line_width(
            layer.width)))  # sometimes lines have negative width?
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
        context.symbol_layer_output_to_input_index_map[
            out] = context.current_symbol_layer

    @staticmethod
    def apply_template_to_LineSymbolLayer_custom_dash(template, layer,
                                                      context: Context):
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
    def append_CartographicLineSymbolLayer(symbol,
                                           layer: CartographicLineSymbol,
                                           context: Context):
        """
        Appends a CartographicLineSymbolLayer to a symbol
        """
        color = ColorConverter.color_to_qcolor(layer.color)
        out = QgsSimpleLineSymbolLayer(color)
        out.setEnabled(layer.enabled)
        out.setLocked(layer.locked)
        if layer.symbol_level != 0xffffffff:
            out.setRenderingPass(layer.symbol_level)
        out.setWidth(context.convert_size(context.fix_line_width(
            layer.width)))  # sometimes lines have negative width?
        out.setWidthUnit(context.units)
        out.setPenJoinStyle(
            ConversionUtils.symbol_pen_to_qpenjoinstyle(layer.join))
        out.setPenCapStyle(
            ConversionUtils.symbol_pen_to_qpencapstyle(layer.cap))
        if layer.template is not None:
            SymbolConverter.apply_template_to_LineSymbolLayer_custom_dash(
                layer.template, out, context)

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
        context.symbol_layer_output_to_input_index_map[
            out] = context.current_symbol_layer

        if layer.decoration is not None:
            DecorationConverter.append_decorations(symbol, layer.decoration,
                                                   context,
                                                   enabled=layer.enabled,
                                                   locked=layer.locked)

    # pylint: disable=too-many-statements,too-many-branches,too-many-locals,too-many-nested-blocks
    @staticmethod
    def append_TemplatedLineSymbolLayer(symbol,
                                        layer: Union[
                                            MarkerLineSymbol, HashLineSymbol],
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
            sub_symbol = SymbolConverter.Symbol_to_QgsSymbol(
                layer.pattern_marker, context)

            # freaking weird logic Arc... !!?!?!
            if isinstance(layer.pattern_marker, MultiLayerSymbol):
                first_angle = ConversionUtils.convert_angle(
                    layer.pattern_marker.layers[0].angle)
                for layer_idx in range(sub_symbol.symbolLayerCount()):
                    sub_symbol_layer = sub_symbol.symbolLayer(layer_idx)

                    original_layer_index = \
                    context.final_symbol_layer_output_to_input_index_map[
                        sub_symbol_layer]

                    original_angle = ConversionUtils.convert_angle(
                        layer.pattern_marker.layers[
                            original_layer_index].angle)

                    if layer_idx == 0:
                        sub_symbol_layer.setAngle(
                            sub_symbol_layer.angle() - original_angle)
                    else:
                        sub_symbol_layer.setAngle(
                            original_angle - first_angle - 90)
            else:
                sub_symbol.setAngle(90)

        elif isinstance(layer, HashLineSymbol):
            sub_symbol = SymbolConverter.Symbol_to_QgsSymbol(layer.line,
                                                             context)

        if (
                len(template.pattern_parts) == 1 and  # pylint: disable=too-many-nested-blocks
                template.pattern_parts[0][1] == 0):
            # special case! (Not described anywhere in ArcMap docs!!)
            # actually means "center of line segment"
            start_symbol = sub_symbol.clone()
            if isinstance(layer, MarkerLineSymbol):
                line = QgsMarkerLineSymbolLayer(True)
                # start_symbol.setAngle(start_symbol.angle() - 90)
            else:
                if HAS_HASHED_LINE_SYMBOL_LAYER:
                    line = QgsHashedLineSymbolLayer(True)
                    line.setHashLength(layer.width)
                    line.setHashLengthUnit(QgsUnitTypes.RenderPoints)
                    line.setHashAngle(
                        ConversionUtils.convert_angle(layer.angle - 90))
                else:
                    if context.unsupported_object_callback:
                        context.push_warning(
                            'Hashed line symbols require QGIS 3.8 or greater',
                            Context.CRITICAL)
                        return
                    else:
                        raise NotImplementedException(
                            'Hashed line symbols require QGIS 3.8 or greater')

            line.setSubSymbol(start_symbol)
            line.setOffset(-context.convert_size(layer.offset))
            line.setOffsetUnit(context.units)

            if Qgis.QGIS_VERSION_INT >= 30900:
                from qgis.core import \
                    QgsTemplatedLineSymbolLayerBase  # pylint: disable=import-outside-toplevel
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
            context.symbol_layer_output_to_input_index_map[
                line] = context.current_symbol_layer
        else:
            current_offset_from_start = 0
            for t in template.pattern_parts:
                if t[0]:
                    # symbol
                    start_symbol = sub_symbol.clone()
                    if isinstance(layer, MarkerLineSymbol):
                        line = QgsMarkerLineSymbolLayer(True)
                        # start_symbol.setAngle(start_symbol.angle() - 90)
                    else:
                        if HAS_HASHED_LINE_SYMBOL_LAYER:
                            line = QgsHashedLineSymbolLayer(True)
                            line.setHashLength(layer.width)
                            line.setHashLengthUnit(QgsUnitTypes.RenderPoints)
                            line.setHashAngle(ConversionUtils.convert_angle(
                                layer.angle - 90))
                        else:
                            if context.unsupported_object_callback:
                                context.push_warning(
                                    'Hashed line symbols require QGIS 3.8 or greater',
                                    Context.CRITICAL)
                                return
                            else:
                                raise NotImplementedException(
                                    'Hashed line symbols require QGIS 3.8 or greater')

                    line.setSubSymbol(start_symbol)
                    line.setOffset(-context.convert_size(layer.offset))
                    line.setOffsetUnit(context.units)
                    line.setInterval(context.convert_size(total_length))
                    line.setIntervalUnit(context.units)
                    line.setOffsetAlongLine(
                        context.convert_size(
                            current_offset_from_start + template.pattern_interval / 2))
                    line.setOffsetAlongLineUnit(context.units)

                    line.setEnabled(layer.enabled)
                    line.setLocked(layer.locked)
                    if layer.symbol_level != 0xffffffff:
                        line.setRenderingPass(layer.symbol_level)

                    symbol.appendSymbolLayer(line)
                    context.symbol_layer_output_to_input_index_map[
                        line] = context.current_symbol_layer

                    current_offset_from_start += template.pattern_interval * t[
                        0]

                if t[1]:
                    # space
                    current_offset_from_start += template.pattern_interval * t[
                        1]

        if layer.decoration is not None:
            DecorationConverter.append_decorations(symbol, layer.decoration,
                                                   context,
                                                   enabled=layer.enabled,
                                                   locked=layer.locked)

    # pylint: enable=too-many-statements,too-many-branches,too-many-locals,too-many-nested-blocks

    @staticmethod
    def append_Marker3DSymbolLayer(symbol, layer: Marker3DSymbol,
                                   context: Context):
        """
        Appends a Marker3DSymbol to a symbol
        """
        context.push_warning('3D marker was converted to a simple marker')
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
            image_path = SymbolConverter.symbol_name_to_filename(
                context.symbol_name,
                context.get_picture_store_folder(), 'png')
            image.save(image_path)

        out = QgsRasterMarkerSymbolLayer(image_path,
                                         context.convert_size(layer.size_z))
        out.setSizeUnit(context.units)
        out.setEnabled(layer.enabled)
        out.setLocked(layer.locked)
        if layer.symbol_level != 0xffffffff:
            out.setRenderingPass(layer.symbol_level)
        symbol.appendSymbolLayer(out)
        context.symbol_layer_output_to_input_index_map[
            out] = context.current_symbol_layer

    @staticmethod
    def append_SimpleMarker3DSymbolLayer(symbol, layer: SimpleMarker3DSymbol,
                                         context: Context):
        """
        Appends a SimpleMarker3DSymbol to a symbol
        """
        context.push_warning('3D simple marker was converted '
                             'to a simple marker')

        marker_type = SymbolConverter.marker_3d_type_to_qgis_type(layer.type)

        # convert size to approximate 2d size, based on ArcMap rendering
        out_size = max(1.5, 6 * math.log(layer.size_z) - 2.5)

        out = QgsSimpleMarkerSymbolLayer(marker_type,
                                         context.convert_size(out_size))
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
                QPointF(context.convert_size(layer.x_offset),
                        -context.convert_size(layer.y_offset)),
                layer.z_rotation))
        out.setOffsetUnit(context.units)

        out.setStrokeStyle(Qt.NoPen)

        symbol.appendSymbolLayer(out)
        context.symbol_layer_output_to_input_index_map[
            out] = context.current_symbol_layer

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
            raise NotImplementedException(
                'Marker type {} not implemented'.format(marker_type))

    @staticmethod
    def marker_3d_type_to_qgis_type(symbol_type):
        """
        Converts simple 3d marker types to corresponding QGIS types
        """
        if symbol_type == SimpleMarker3DSymbol.TETRAHEDRON:
            return QgsSimpleMarkerSymbolLayerBase.Triangle
        elif symbol_type == SimpleMarker3DSymbol.CUBE:
            return QgsSimpleMarkerSymbolLayerBase.Square
        elif symbol_type in (
        SimpleMarker3DSymbol.CONE, SimpleMarker3DSymbol.CYLINDER,
        SimpleMarker3DSymbol.SPHERE,
        SimpleMarker3DSymbol.SPHERE_FRAME):
            return QgsSimpleMarkerSymbolLayerBase.Circle
        elif symbol_type == SimpleMarker3DSymbol.DIAMOND:
            return QgsSimpleMarkerSymbolLayerBase.Diamond
        else:
            raise NotImplementedException(
                'Marker type {} not implemented'.format(symbol_type))

    @staticmethod
    def append_SimpleMarkerSymbolLayer(symbol, layer: SimpleMarkerSymbol,
                                       context: Context):
        """
        Appends a SimpleMarkerSymbolLayer to a symbol
        """
        marker_type = SymbolConverter.marker_type_to_qgis_type(layer.type)
        out = QgsSimpleMarkerSymbolLayer(marker_type,
                                         context.convert_size(layer.size))

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

        out.setOffset(QPointF(context.convert_size(layer.x_offset),
                              -context.convert_size(layer.y_offset)))
        out.setOffsetUnit(context.units)

        if layer.outline_enabled:
            outline_color = ColorConverter.color_to_qcolor(layer.outline_color)
            if not stroke_only_symbol:
                out.setStrokeColor(outline_color)
                if not layer.color.is_null:
                    # Better match to how ESRI renders this if we divide the outline width by 2,
                    # because ESRI renders the stroke below the symbol. Maybe we should split this
                    # into two layers?
                    out.setStrokeWidth(
                        context.convert_size(layer.outline_width / 2))
                else:
                    out.setStrokeWidth(
                        context.convert_size(layer.outline_width))
                out.setStrokeWidthUnit(context.units)
                if layer.outline_width <= 0:
                    out.setStrokeStyle(Qt.NoPen)
            else:
                # for stroke-only symbols, we need to add the outline as an additional
                # symbol layer
                outline_layer = QgsSimpleMarkerSymbolLayer(marker_type,
                                                           context.convert_size(
                                                               layer.size))
                outline_layer.setSizeUnit(context.units)
                outline_layer.setStrokeColor(outline_color)
                outline_layer.setStrokeWidth(context.convert_size(
                    context.fix_line_width(layer.outline_width)))
                outline_layer.setStrokeWidthUnit(context.units)
                symbol.appendSymbolLayer(outline_layer)
                context.symbol_layer_output_to_input_index_map[
                    outline_layer] = context.current_symbol_layer
        elif not stroke_only_symbol:
            out.setStrokeStyle(Qt.NoPen)

        symbol.appendSymbolLayer(out)
        context.symbol_layer_output_to_input_index_map[
            out] = context.current_symbol_layer

    @staticmethod
    def round_dict(val, places):
        """
        Rounds values in dictionary, recursively
        """
        if isinstance(val, dict):
            res = {}
            for k, v in val.items():
                res[k] = SymbolConverter.round_dict(v, places)
            return res
        elif isinstance(val, (list, tuple)):
            return [SymbolConverter.round_dict(v, places) for v in val]
        elif isinstance(val, float):
            return round(val, places)
        else:
            return val

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
        out.setStrokeColor(
            color)  # why not, makes the symbol a bit easier to modify in qgis

        out.setOffset(
            ConversionUtils.adjust_offset_for_rotation(
                QPointF(context.convert_size(layer.x_offset),
                        -context.convert_size(layer.y_offset)),
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
        context.symbol_layer_output_to_input_index_map[
            out] = context.current_symbol_layer

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
            68: {'shape': QgsSimpleMarkerSymbolLayerBase.Cross2,
                 'outline_only': True,
                 'shape_size_factor': 0.8919171482489955,
                 'stroke_size_factor': 3.581800012565442},
            69: {'shape': QgsSimpleMarkerSymbolLayerBase.Cross,
                 'outline_only': True,
                 'shape_size_factor': 0.8919171482489955,
                 'stroke_size_factor': 4.88062371717723},
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
            80: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                 'outline_only': True,
                 'shape_size_factor': 0.9571292527171059,
                 'stroke_size_factor': 2.90101098080052,
                 'central_overlay': QgsSimpleMarkerSymbolLayerBase.Circle,
                 'overlay_size_factor': 2.1608275432262554,
                 'overlay_angle': 0},
            82: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                 'outline_only': True,
                 'shape_size_factor': 0.9736180059208173,
                 'stroke_size_factor': 1.7810108595221255,
                 'central_overlay': QgsSimpleMarkerSymbolLayerBase.Circle,
                 'overlay_size_factor': 1.7135893730603813,
                 'central_overlay_outline_only': True,
                 'overlay_angle': 0},
            83: {'shape': QgsSimpleMarkerSymbolLayerBase.Square,
                 'outline_only': True,
                 'shape_size_factor': 0.9967022604060128,
                 'stroke_size_factor': 1.087677451111691,
                 'central_overlay': QgsSimpleMarkerSymbolLayerBase.Cross2,
                 'overlay_size_factor': 0.8836814401705497,
                 'overlay_angle': 0},
            85: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                 'outline_only': True,
                 'shape_size_factor': 0.9736180059208173,
                 'stroke_size_factor': 1.7810108595221255,
                 'central_overlay': QgsSimpleMarkerSymbolLayerBase.EquilateralTriangle,
                 'overlay_size_factor': 0.8552535423790505,
                 'central_overlay_outline_only': True,
                 'overlay_angle': 0},
            86: {'shape': QgsSimpleMarkerSymbolLayerBase.EquilateralTriangle,
                 'outline_only': True,
                 'shape_size_factor': 1.0445196446967753,
                 'stroke_size_factor': 1.7810108595221255,
                 'central_overlay': QgsSimpleMarkerSymbolLayerBase.EquilateralTriangle,
                 'overlay_size_factor': 0.4931118372114387,
                 'overlay_y_offset_factor': 1.0354584362120463,
                 'overlay_angle': 0},
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
            90: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                 'outline_only': True,
                 'shape_size_factor': 0.9736180059208173,
                 'stroke_size_factor': 1.7810108595221255,
                 'central_overlay': QgsSimpleMarkerSymbolLayerBase.Star,
                 'overlay_size_factor': 0.4780225994961215,
                 'overlay_angle': 0},
            91: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                 'outline_only': True,
                 'shape_size_factor': 1.0065955123282395,
                 'stroke_size_factor': 0.7676774164607211,
                 'central_overlay': QgsSimpleMarkerSymbolLayerBase.Star,
                 'overlay_size_factor': 0.3663622404027745,
                 'overlay_angle': 0},
            92: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                 'outline_only': True,
                 'shape_size_factor': 1.0065955123282395,
                 'stroke_size_factor': 0.7676774164607211,
                 'central_overlay': QgsSimpleMarkerSymbolLayerBase.Star,
                 'overlay_size_factor': 0.894485560438875,
                 'overlay_angle': 0},
            93: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                 'outline_only': True,
                 'shape_size_factor': 1.0065955123282395,
                 'stroke_size_factor': 0.7676774164607211,
                 'central_overlay': QgsSimpleMarkerSymbolLayerBase.Star,
                 'overlay_size_factor': 0.894485560438875,
                 'overlay_stroke_factor': 1.55,
                 'central_overlay_outline_only': True,
                 'overlay_angle': 0},
            96: {'shape': QgsSimpleMarkerSymbolLayerBase.Star,
                 'outline_only': True,
                 'shape_size_factor': 1.0065955123282395,
                 'stroke_size_factor': 0.7676774164607211,
                 'central_overlay': QgsSimpleMarkerSymbolLayerBase.Star,
                 'overlay_size_factor': 0.2562107512450968,
                 'overlay_y_offset_factor': 1.2943551873662755,
                 'overlay_angle': 0},
            94: {'shape': QgsSimpleMarkerSymbolLayerBase.Star},
            95: {'shape': QgsSimpleMarkerSymbolLayerBase.Star,
                 'outline_only': True},
            169: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                  'outline_only': True,
                  'shape_size_factor': 1.0296797668134352,
                  'stroke_size_factor': 0.927677433786206,
                  'central_overlay': QgsSimpleMarkerSymbolLayerBase.Cross,
                  'overlay_size_factor': 0.7782984300309329,
                  'overlay_stroke_factor': 5.229436512101896,
                  'central_overlay_outline_only': True,
                  'overlay_angle': 0},
            170: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                  'outline_only': True,
                  'shape_size_factor': 1.0296797668134352,
                  'stroke_size_factor': 0.927677433786206,
                  'central_overlay': QgsSimpleMarkerSymbolLayerBase.Cross,
                  'overlay_size_factor': 0.7782984300309329,
                  'overlay_stroke_factor': 5.229436512101896,
                  'central_overlay_outline_only': True,
                  'overlay_angle': 45},
            171: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                  'outline_only': True,
                  'shape_size_factor': 1.0296797668134352},
            172: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                  'shape_size_factor': 0.9165104847042012},
            183: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                  'shape_size_factor': 0.9451800361718738},
            185: {'shape': QgsSimpleMarkerSymbolLayerBase.EquilateralTriangle,
                  'shape_size_factor': 0.9451800361718738},
            196: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                  'shape_size_factor': 0.9451800361718738},
            199: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                  'shape_size_factor': 0.5770026383764989},
            200: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                  'shape_size_factor': 0.6418863601191265},
            201: {'shape': QgsSimpleMarkerSymbolLayerBase.Square,
                  'shape_size_factor': 0.9390556014511079},
            203: {'shape': QgsSimpleMarkerSymbolLayerBase.Cross,
                  'outline_only': True,
                  'shape_size_factor': 0.9006464914345718,
                  'stroke_size_factor': 4.880623717177232},
            204: {'shape': QgsSimpleMarkerSymbolLayerBase.Cross,
                  'outline_only': True,
                  'shape_size_factor': 0.9006464914345718,
                  'stroke_size_factor': 4.541800142061113},
            205: {'shape': QgsSimpleMarkerSymbolLayerBase.Cross,
                  'outline_only': True,
                  'shape_size_factor': 0.9268345209913009,
                  'stroke_size_factor': 3.920623587681562},
            206: {'shape': QgsSimpleMarkerSymbolLayerBase.Cross,
                  'outline_only': True,
                  'shape_size_factor': 0.9442932073624539,
                  'stroke_size_factor': 3.2994470333020107},
            207: {'shape': QgsSimpleMarkerSymbolLayerBase.Cross,
                  'outline_only': True,
                  'shape_size_factor': 0.963497762370722,
                  'stroke_size_factor': 2.6217998830697717},
            208: {'shape': QgsSimpleMarkerSymbolLayerBase.Cross,
                  'outline_only': True,
                  'shape_size_factor': 0.9757188428305291,
                  'stroke_size_factor': 2.17003511624828},
            209: {'shape': QgsSimpleMarkerSymbolLayerBase.Cross,
                  'outline_only': True,
                  'shape_size_factor': 0.9931775292016818,
                  'stroke_size_factor': 1.7182703494267881},
            210: {'shape': QgsSimpleMarkerSymbolLayerBase.Cross,
                  'outline_only': True,
                  'shape_size_factor': 1.0071444782986039,
                  'stroke_size_factor': 1.2665055826052964},
            211: {'shape': QgsSimpleMarkerSymbolLayerBase.Cross,
                  'outline_only': True,
                  'shape_size_factor': 1.019365558758411,
                  'stroke_size_factor': 0.8712114116364911},
        },
        'ESRI ArcGIS TDN': {
            35: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                 'shape_size_factor': 0.12932914989379118,
                 },
            39: {'shape': QgsSimpleMarkerSymbolLayerBase.Line,
                 'angle': 90,
                 'shape_size_factor': 0.7439879243257865,
                 'outline_only': True,
                 'stroke_size_factor': 2.653333333333333,
                 },
            50: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                 'shape_size_factor': 0.33152505554488476,
                 'outline_only': True,
                 'stroke_size_factor': 2.706666666666666,
                 },
            52: {'shape': QgsSimpleMarkerSymbolLayerBase.Cross,
                 'shape_size_factor': 0.4115613882341978,
                 'outline_only': True,
                 'stroke_size_factor': 2.6799999999999993
                 },
            53: {'shape': QgsSimpleMarkerSymbolLayerBase.EquilateralTriangle,
                 'shape_size_factor': 0.326578429600613,
                 'outline_only': True,
                 'stroke_size_factor': 1.7733333333333332,
                 'vertical_offset_factor': 1.2457202154021212
                 },
            55: {'ellipse_marker_type': 'rectangle',
                 'outline_only': True,
                 'width_factor': 0.17360565193140656,
                 'height_factor': 0.09988725061195887,
                 'stroke_scale': 0.8392987532397534
                 },
            71: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                 'shape_size_factor': 0.4741183593831859,
                 },
            72: {'shape': QgsSimpleMarkerSymbolLayerBase.Square,
                 'shape_size_factor': 0.6349181134602188,
                 'outline_only': True,
                 'stroke_size_factor': 3.3733333333333326
                 },
            86: {'shape': QgsSimpleMarkerSymbolLayerBase.Square,
                 'shape_size_factor': 0.6122842583476866,
                 },
            87: {'ellipse_marker_type': 'rectangle',
                 'width_factor': 0.1909582764126922,
                 'height_factor': 0.11346755240505034,
                 },
            88: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                 'shape_size_factor': 0.31341791819885095,
                 },
            89: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                 'shape_size_factor': 0.35131156670274644,
                 'outline_only': True,
                 'stroke_size_factor': 1.16,
                 },
            93: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                 'shape_size_factor': 0.04784723605384667,
                 },
            95: {'ellipse_marker_type': 'circle',
                 'width_factor': 0.17360565193140656,
                 'height_factor': 0.06970876571721113,
                 'outline_only': True,
                 'stroke_scale': 1.2126321250821663
                 },
            96: {'ellipse_marker_type': 'circle',
                 'width_factor': 0.2022752054222263,
                 'height_factor': 0.09611493009780375,
                 },
            97: {'ellipse_marker_type': 'circle',
                 'width_factor': 0.17134226612949977,
                 'height_factor': 0.08027123146944817,
                 },
        },
        'ESRI ArcPad': {
            33: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                 'shape_size_factor': 0.9344231669332914,
                 },
            34: {'shape': QgsSimpleMarkerSymbolLayerBase.Square,
                 'shape_size_factor': 0.9344231669332914,
                 },
            35: {'shape': QgsSimpleMarkerSymbolLayerBase.EquilateralTriangle,
                 'shape_size_factor': 0.990491198259151,
                 },
            37: {'ellipse_marker_type': 'diamond',
                 'width_factor': 0.19685181337401686,
                 'height_factor': 0.34262196532114203,
                 },
            38: {'shape': QgsSimpleMarkerSymbolLayerBase.Star,
                 'shape_size_factor': 0.990491198259151,
                 },
        },
        'ESRI Arrowhead': {
            62: {'ellipse_marker_type': 'triangle',
                 'width_factor': 0.3426218270750293,
                 'height_factor': 0.2055731791926852,
                 'angle': 90,
                 },
            63: {'ellipse_marker_type': 'triangle',
                 'width_factor': 0.2180328646217991,
                 'height_factor': 0.39245907681960146,
                 'angle': 90,
                 },
            190: {'ellipse_marker_type': 'triangle',
                  'width_factor': 0.3426218270750293,
                  'height_factor': 0.2055731791926852,
                  'angle': 90,
                  },
            191: {'ellipse_marker_type': 'triangle',
                  'width_factor': 0.2180328646217991,
                  'height_factor': 0.39245907681960146,
                  'angle': 270,
                  },
        },
        'ESRI Business': {
            33: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                 'shape_size_factor': 0.97180268508445,
                 },
            41: {'shape': QgsSimpleMarkerSymbolLayerBase.Star,
                 'shape_size_factor': 1.2205416261711395,
                 },
            45: {'ellipse_marker_type': 'diamond',
                 'width_factor': 0.19809839397240805,
                 'height_factor': 0.34262299093638626,
                 },
            190: {'ellipse_marker_type': 'circle',
                  'width_factor': 0.5045902487976431,
                  'height_factor': 0.34262299093638626,
                  },
            191: {'ellipse_marker_type': 'circle',
                  'width_factor': 0.4859017210643971,
                  'height_factor': 0.3363934820102702,
                  },
        },
        'ESRI Geology USGS 95-525': {
            35: {'shape': QgsSimpleMarkerSymbolLayerBase.Line,
                 'outline_only': True,
                 'shape_size_factor': 0.15666864070024933,
                 'stroke_size_factor': 1.433351703353058},
        },
        'ESRI Cartography': {
            72: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                 'outline_only': True,
                 'shape_size_factor': 0.939134942311759,
                 'stroke_size_factor': 2.829715050724875,
                 'central_overlay': QgsSimpleMarkerSymbolLayerBase.Circle,
                 'overlay_size_factor': 1.6504965013928692,
                 'overlay_stroke_factor': 1.0000002023905774,
                 'central_overlay_outline_only': True,
                 },
            73: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                 'outline_only': True,
                 'shape_size_factor': 0.8986625474008189,
                 'stroke_size_factor': 3.9642602704644765,
                 'central_overlay': QgsSimpleMarkerSymbolLayerBase.Circle,
                 'overlay_size_factor': 1.5753070239000497,
                 'overlay_stroke_factor': 1.0000002023905774,
                 'central_overlay_outline_only': True,
                 },
            74: {'shape': QgsSimpleMarkerSymbolLayerBase.Line,
                 'outline_only': True,
                 'shape_size_factor': 0.8986625474008189,
                 'stroke_size_factor': 3.9642602704644765,
                 'cap_style': Qt.RoundCap
                 },
            77: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                 'outline_only': True,
                 'shape_size_factor': 0.2106318339148362,
                 'stroke_size_factor': 3.0410493984906326
                 },
            78: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                 'shape_size_factor': 0.29211369052653874
                 },
            179: {'shape': QgsSimpleMarkerSymbolLayerBase.Line,
                  'outline_only': True,
                  'shape_size_factor': 0.9674656187494172,
                  'stroke_size_factor': 1.8697152494067508,
                  'cap_style': Qt.RoundCap
                  },
            202: {'shape': QgsSimpleMarkerSymbolLayerBase.Star,
                  'shape_size_factor': 1.2056605537118097
                  },
        },
        'ESRI Caves 1': {
            33: {'shape': QgsSimpleMarkerSymbolLayerBase.Square,
                 'shape_size_factor': 1.1213107904820578,
                 },
            39: {'shape': QgsSimpleMarkerSymbolLayerBase.EquilateralTriangle,
                 'shape_size_factor': 1.0216387202169859,
                 },
            42: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                 'shape_size_factor': 1.1213107904820578,
                 },
            114: {'ellipse_marker_type': 'triangle',
                  'width_factor': 0.2616392931934454,
                  'height_factor': 0.180655765520134,
                  },
            116: {'ellipse_marker_type': 'triangle',
                  'width_factor': 0.17442619546229693,
                  'height_factor': 0.2803277186845398,
                  },
            212: {'shape': QgsSimpleMarkerSymbolLayerBase.Square,
                  'shape_size_factor': 1.0714747553495219,
                  },
        },
        'ESRI Caves 2': {
            36: {'ellipse_marker_type': 'square',
                 'width_factor': 0.3768851723381773,
                 'height_factor': 0.2566556002178454,
                 },
            84: {'ellipse_marker_type': 'square',
                 'width_factor': 0.38622943280937183,
                 'height_factor': 0.19436064597110914,
                 },
            238: {'ellipse_marker_type': 'triangle',
                  'width_factor': 0.2616392931934454,
                  'height_factor': 0.180655765520134,
                  },

        },
        'ESRI Caves 3': {
            49: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                 'shape_size_factor': 0.5733910903740004,
                 },
            53: {'shape': QgsSimpleMarkerSymbolLayerBase.Square,
                 'shape_size_factor': 0.6410581523442068,
                 },
            55: {'shape': QgsSimpleMarkerSymbolLayerBase.Square,
                 'shape_size_factor': 1.003762106960008,
                 },
            60: {'shape': QgsSimpleMarkerSymbolLayerBase.Square,
                 'shape_size_factor': 1.003762106960008,
                 },
            62: {'shape': QgsSimpleMarkerSymbolLayerBase.Square,
                 'shape_size_factor': 1.003762106960008,
                 },
            64: {'ellipse_marker_type': 'square',
                 'width_factor': 0.3416168081587184,
                 'height_factor': 0.17713463966317866,
                 },
            66: {'ellipse_marker_type': 'square',
                 'width_factor': 0.4242796407502108,
                 'height_factor': 0.2977548942909622,
                 },
            68: {'ellipse_marker_type': 'square',
                 'width_factor': 0.4242796407502108,
                 'height_factor': 0.2977548942909622,
                 },
        },
        'ESRI Climate & Precipitation': {
            37: {'shape': QgsSimpleMarkerSymbolLayerBase.EquilateralTriangle,
                 'shape_size_factor': 0.4597061750363063,
                 },
            38: {'shape': QgsSimpleMarkerSymbolLayerBase.EquilateralTriangle,
                 'shape_size_factor': 0.4597061750363063,
                 'angle': 180,
                 },
            43: {'shape': QgsSimpleMarkerSymbolLayerBase.SemiCircle,
                 'shape_size_factor': 0.45347343460731465,
                 },
            44: {'shape': QgsSimpleMarkerSymbolLayerBase.SemiCircle,
                 'shape_size_factor': 0.45347343460731465,
                 'angle': 180,
                 },
            86: {'ellipse_marker_type': 'circle',
                 'width_factor': 0.10965477792748986,
                 'height_factor': 0.10290679066146569,
                 },
            96: {'ellipse_marker_type': 'triangle',
                 'width_factor': 0.37113924836996565,
                 'height_factor': 0.198222096765938,
                 },
            120: {'shape': QgsSimpleMarkerSymbolLayerBase.SemiCircle,
                  'shape_size_factor': 0.45347343460731465,
                  },
            197: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                  'shape_size_factor': 0.3458338988394936,
                  'vertical_offset_factor': 1.575,
                  'horizontal_offset_factor': .1,
                  },
            202: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                  'shape_size_factor': 0.3458338988394936,
                  'vertical_offset_factor': 1.575,
                  'horizontal_offset_factor': .1,
                  },
            208: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                  'shape_size_factor': 0.41331368397890705,
                  },
            211: {'ellipse_marker_type': 'triangle',
                  'width_factor': 0.3458342996174679,
                  'height_factor': 0.26148446807421605,
                  },
            228: {'ellipse_marker_type': 'triangle',
                  'width_factor': 0.3458342996174679,
                  'height_factor': 0.12230725119600427,
                  'angle': 90,
                  'vertical_offset_factor': 0.1,
                  },
        },
        'ESRI AMFM Electric': {
            33: {'shape': QgsSimpleMarkerSymbolLayerBase.Square,
                 'shape_size_factor': 1.0153634389208162
                 },
            48: {'shape': QgsSimpleMarkerSymbolLayerBase.EquilateralTriangle,
                 'shape_size_factor': 1.078738211080188
                 },
            54: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                 'shape_size_factor': 0.5365451835215594
                 },
            58: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                 'shape_size_factor': 0.19944873314152206
                 },
            88: {'ellipse_marker_type': 'rectangle',
                 'width_factor': 0.38364351448646505,
                 'height_factor': 0.19917766074151325,
                 },
            93: {'shape': QgsSimpleMarkerSymbolLayerBase.Square,
                 'shape_size_factor': 1.086424111820078
                 },
            94: {'ellipse_marker_type': 'rectangle',
                 'width_factor': 0.2939387713086604,
                 'height_factor': 0.22409564370249616,
                 },
            95: {'ellipse_marker_type': 'rectangle',
                 'width_factor': 0.3936107081728878,
                 'height_factor': 0.19809796453981388,
                 },
            100: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                  'shape_size_factor': 0.9973439687729347
                  },
            172: {'ellipse_marker_type': 'rectangle',
                  'width_factor': 0.4572450103646429,
                  'height_factor': 0.19917766074151325,
                  },
            205: {'ellipse_marker_type': 'rectangle',
                  'width_factor': 0.3064912492840521,
                  'height_factor': 0.3737697444147432,
                  },
            206: {'ellipse_marker_type': 'rectangle',
                  'width_factor': 0.20308198376704445,
                  'height_factor': 0.3874757421168326,
                  },
            219: {'ellipse_marker_type': 'rectangle',
                  'width_factor': 0.5108184602276327,
                  'height_factor': 0.2740977143665235,
                  },
            221: {'ellipse_marker_type': 'rectangle',
                  'width_factor': 0.29278693448752136,
                  'height_factor': 0.14701628606616177,
                  },
            223: {'ellipse_marker_type': 'rectangle',
                  'width_factor': 0.1868852773324604,
                  'height_factor': 0.3675410266408507,
                  },
            226: {'ellipse_marker_type': 'rectangle',
                  'width_factor': 0.21803282355453715,
                  'height_factor': 0.32767216951370753,
                  },
            227: {'ellipse_marker_type': 'rectangle',
                  'width_factor': 0.21429511800788795,
                  'height_factor': 0.32767216951370753,
                  },
            228: {'shape': QgsSimpleMarkerSymbolLayerBase.Hexagon,
                  'shape_size_factor': 1.2450068618099817
                  },
            229: {'ellipse_marker_type': 'rectangle',
                  'width_factor': 0.3463607139894933,
                  'height_factor': 0.2691147856082161,
                  },
            230: {'ellipse_marker_type': 'rectangle',
                  'width_factor': 0.46098368408673573,
                  'height_factor': 0.23049183026629622,
                  },
            231: {'ellipse_marker_type': 'rectangle',
                  'width_factor': 0.3812459657582193,
                  'height_factor': 0.18314756242781374,
                  },
            232: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                  'shape_size_factor': 0.9468841308974395
                  },
            233: {'ellipse_marker_type': 'rectangle',
                  'width_factor': 0.4746886044244495,
                  'height_factor': 0.31521315166147534,
                  },
            234: {'ellipse_marker_type': 'rectangle',
                  'width_factor': 0.4074099045847637,
                  'height_factor': 0.27783609810477866,
                  },
        },

        'ESRI AMFM Gas': {
            33: {'ellipse_marker_type': 'rectangle',
                 'width_factor': 0.4535082729934374,
                 'height_factor': 0.3550820087886185,
                 },
            37: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                 'shape_size_factor': 0.9718012654082938
                 },
            39: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                 'shape_size_factor': 0.4049177130453956
                 },
            46: {'shape': QgsSimpleMarkerSymbolLayerBase.EquilateralTriangle,
                 'shape_size_factor': 1.1026220801390003,
                 'angle': 90,
                 'vertical_offset_factor': -0.05,
                 },
            165: {'shape': QgsSimpleMarkerSymbolLayerBase.Square,
                  'outline_only': True,
                  'shape_size_factor': 0.9742110179012407,
                  'stroke_size_factor': 0.9533518026939961,
                  'central_overlay': QgsSimpleMarkerSymbolLayerBase.Cross,
                  'overlay_size_factor': 0.8603691048301341,
                  'overlay_stroke_factor': 1.0000002023905774,
                  'central_overlay_outline_only': True,
                  },
            169: {'shape': QgsSimpleMarkerSymbolLayerBase.Square,
                  'shape_size_factor': 0.9718025113089495,
                  },
        },
        'ESRI AMFM Sewer': {
            35: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                 'shape_size_factor': 0.7350813867593337
                 },
            39: {'shape': QgsSimpleMarkerSymbolLayerBase.EquilateralTriangle,
                 'shape_size_factor': 0.8285239359236557,
                 'vertical_offset_factor': -0.06,
                 },
            41: {'ellipse_marker_type': 'rectangle',
                 'width_factor': 0.032393448070959806,
                 'height_factor': 0.25914757132643035,
                 },
            46: {'ellipse_marker_type': 'rectangle',
                 'width_factor': 0.12708198858607309,
                 'height_factor': 0.25914757132643035,
                 },
            50: {'ellipse_marker_type': 'rectangle',
                 'width_factor': 0.12708198858607309,
                 'height_factor': 0.25914757132643035,
                 },
            72: {'shape': QgsSimpleMarkerSymbolLayerBase.Diamond,
                 'shape_size_factor': 0.7350813867593335
                 },
            73: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                 'shape_size_factor': 0.7350813867593335
                 },
            103: {'shape': QgsSimpleMarkerSymbolLayerBase.Square,
                  'shape_size_factor': 0.728851883481712
                  },
            # TODO
            104: {'shape': QgsSimpleMarkerSymbolLayerBase.CrossFill,
                  'shape_size_factor': 0.728851883481712
                  },
            108: {'shape': QgsSimpleMarkerSymbolLayerBase.Square,
                  'shape_size_factor': 0.7238682808596149
                  },
            110: {'ellipse_marker_type': 'rectangle',
                  'width_factor': 0.2579016827187954,
                  'height_factor': 0.12708198209276872,
                  },
            112: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                  'shape_size_factor': 0.317704667158695
                  },
            113: {'shape': QgsSimpleMarkerSymbolLayerBase.EquilateralTriangle,
                  'shape_size_factor': 0.8409829424788986,
                  'angle': 180,
                  'vertical_offset_factor': -0.055,
                  },
            114: {'ellipse_marker_type': 'rectangle',
                  'width_factor': 0.2579016827187954,
                  'height_factor': 0.15200001779723318,
                  },
            115: {'ellipse_marker_type': 'rectangle',
                  'width_factor': 0.0660327979908027,
                  'height_factor': 0.25914757132643035,
                  },
            116: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                  'shape_size_factor': 0.36131119010204527
                  },
            117: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                  'shape_size_factor': 0.7350813867593335
                  },
            118: {'shape': QgsSimpleMarkerSymbolLayerBase.Square,
                  'shape_size_factor': 0.7313436847927607
                  },
            120: {'shape': QgsSimpleMarkerSymbolLayerBase.Diamond,
                  'shape_size_factor': 0.7313436847927607
                  },
            121: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                  'shape_size_factor': 0.7350813867593335
                  },
            124: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                  'shape_size_factor': 0.7350813867593335
                  },
            161: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                  'shape_size_factor': 0.7350813867593335
                  },
            162: {'ellipse_marker_type': 'rectangle',
                  'width_factor': 0.2579016827187954,
                  'height_factor': 0.15200001779723318,
                  },
            164: {'ellipse_marker_type': 'rectangle',
                  'width_factor': 0.06727869983968576,
                  'height_factor': 0.2566557677559839,
                  },
            165: {'ellipse_marker_type': 'rectangle',
                  'width_factor': 0.06727869983968576,
                  'height_factor': 0.2566557677559839,
                  },
            234: {'ellipse_marker_type': 'rectangle',
                  'width_factor': 0.4074099045847637,
                  'height_factor': 0.27783609810477866,
                  },

        },
        'ESRI AMFM Water': {
            34: {'shape': QgsSimpleMarkerSymbolLayerBase.Square,
                 'shape_size_factor': 1.0527860539180285,
                 },
            37: {'shape': QgsSimpleMarkerSymbolLayerBase.Star,
                 'shape_size_factor': 1.2205421269352341,
                 },
            38: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                 'shape_size_factor': 1.2205421269352341,
                 },
            51: {'ellipse_marker_type': 'rectangle',
                 'width_factor': 0.45724597854008653,
                 'height_factor': 0.3550820087886185,
                 },
            52: {'shape': QgsSimpleMarkerSymbolLayerBase.Square,
                 'shape_size_factor': 0.9780317355888125,
                 },
            82: {'ellipse_marker_type': 'rectangle',
                 'width_factor': 0.3675410454205056,
                 'height_factor': 0.29403282131268055,
                 },
            83: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                 'shape_size_factor': 0.4859011170441234,
                 },
            84: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                 'shape_size_factor': 0.1,
                 },
            86: {'ellipse_marker_type': 'rectangle',
                 'width_factor': 0.2554098790210293,
                 'height_factor': 0.1532459195824564,
                 'horizontal_offset_factor': -1,
                 },
            88: {'ellipse_marker_type': 'rectangle',
                 'width_factor': 0.45475417484232045,
                 'height_factor': 0.3550820087886185,
                 },
            91: {'ellipse_marker_type': 'rectangle',
                 'width_factor': 0.4834099173666311,
                 'height_factor': 0.3737705355669668,
                 },
            95: {'shape': QgsSimpleMarkerSymbolLayerBase.EquilateralTriangle,
                 'shape_size_factor': 0.8409829424788986,
                 'angle': 0,
                 'vertical_offset_factor': -0.055,
                 },
            96: {'shape': QgsSimpleMarkerSymbolLayerBase.EquilateralTriangle,
                 'shape_size_factor': 1.0652450604732717,
                 'angle': 270,
                 'vertical_offset_factor': -0.055,
                 },
            97: {'shape': QgsSimpleMarkerSymbolLayerBase.EquilateralTriangle,
                 'shape_size_factor': 1.0652450604732717,
                 'angle': 90,
                 'vertical_offset_factor': -0.055,
                 },
            108: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                  'shape_size_factor': 0.4859011170441234,
                  },
            197: {'shape': QgsSimpleMarkerSymbolLayerBase.Star,
                  'shape_size_factor': 1.2205421269352341,
                  },
            198: {'shape': QgsSimpleMarkerSymbolLayerBase.EquilateralTriangle,
                  'shape_size_factor': 1.1208701326813666,
                  'angle': 270,
                  'vertical_offset_factor': -0.055,
                  },
            202: {'shape': QgsSimpleMarkerSymbolLayerBase.Hexagon,
                  'shape_size_factor': 1.0154728186795665,
                  'angle': 30,
                  },
            205: {'shape': QgsSimpleMarkerSymbolLayerBase.Square,
                  'shape_size_factor': 0.9112477418018482,
                  },
            206: {'shape': QgsSimpleMarkerSymbolLayerBase.Square,
                  'outline_only': True,
                  'shape_size_factor': 0.9854471388522006,
                  'stroke_size_factor': 2.309715072769748,
                  },
            214: {'shape': QgsSimpleMarkerSymbolLayerBase.Square,
                  'outline_only': True,
                  'shape_size_factor': 0.9674656187494172,
                  'stroke_size_factor': 1.8697152494067508,
                  'central_overlay': QgsSimpleMarkerSymbolLayerBase.Circle,
                  'overlay_size_factor': 0.8603691048301341,
                  'overlay_stroke_factor': 1.0000002023905774
                  },
            216: {'ellipse_marker_type': 'triangle',
                  'width_factor': 0.19934429582129118,
                  'height_factor': 0.44229513375424406,
                  'angle': 90,
                  },
            222: {'shape': QgsSimpleMarkerSymbolLayerBase.EquilateralTriangle,
                  'shape_size_factor': 1.096392576861379,
                  'vertical_offset_factor': -0.055,
                  },
            231: {'shape': QgsSimpleMarkerSymbolLayerBase.Diamond,
                  'shape_size_factor': 0.9842615178641925,
                  },
        },
        'ESRI Fire Incident NFPA': {
            172: {'shape': QgsSimpleMarkerSymbolLayerBase.Square,
                  'outline_only': True,
                  'shape_size_factor': 1.0861846438215081,
                  'stroke_size_factor': 1.3460789941423195,
                  'central_overlay': QgsSimpleMarkerSymbolLayerBase.Circle,
                  'overlay_size_factor': 2.965674412261938,
                  'overlay_stroke_factor': 1.0000002023905774,
                  'central_overlay_outline_only': True,
                  },
        },
        'ESRI Geometric Symbols': {
            36: {'shape': QgsSimpleMarkerSymbolLayerBase.EquilateralTriangle,
                 'shape_size_factor': 1.0583678399557281,
                 'vertical_offset_factor': 0
                 },
        },
        'ESRI Commodities': {
            36: {'shape': QgsSimpleMarkerSymbolLayerBase.Line,
                 'outline_only': True,
                 'angle': 90,
                 'shape_size_factor': 0.5559962704881921,
                 'stroke_size_factor': 2.087897022433597,
                 },
            39: {'shape': QgsSimpleMarkerSymbolLayerBase.Square,
                 'outline_only': True,
                 'shape_size_factor': 0.9607202195975937,
                 'stroke_size_factor': 2.087897022433597,
                 },
            40: {'shape': QgsSimpleMarkerSymbolLayerBase.Square,
                 'shape_size_factor': 0.9384978866361668
                 },
            41: {'ellipse_marker_type': 'diamond',
                 'outline_only': True,
                 'width_factor': 0.39097001543154347,
                 'height_factor': 0.23183501818109928,
                 'stroke_scale': 0.9253588831024798},
            42: {'ellipse_marker_type': 'diamond',
                 'width_factor': 0.4230689544408402,
                 'height_factor': 0.25529193505688796
                 },
            47: {'shape': QgsSimpleMarkerSymbolLayerBase.EquilateralTriangle,
                 'shape_size_factor': 1.24343767782908,
                 'outline_only': True,
                 'stroke_size_factor': 1.9449208614717124
                 },
            48: {'shape': QgsSimpleMarkerSymbolLayerBase.EquilateralTriangle,
                 'shape_size_factor': 1.24343767782908
                 },
            50: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                 'shape_size_factor': 0.9708757925601526,
                 'outline_only': True,
                 'stroke_size_factor': 1.9449208614717124
                 },
            51: {'shape': QgsSimpleMarkerSymbolLayerBase.Circle,
                 'shape_size_factor': 0.9384978866361668
                 },
        },
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
            173: {'shape': QgsSimpleMarkerSymbolLayerBase.SquareWithCorners,
                  'outline_only': True,
                  'shape_size_factor': 1.093806079589203},
            176: {'shape': QgsSimpleMarkerSymbolLayerBase.Octagon,
                  'outline_only': True,
                  'shape_size_factor': 1.0617429232013191},
        })

        ESRI_FONTS_TO_QGIS_MARKERS['ESRI AMFM Electric'].update({
            215: {'shape': QgsSimpleMarkerSymbolLayerBase.Octagon,
                  'shape_size_factor': 1.036381918330409
                  },
        })

    if Qgis.QGIS_VERSION_INT >= 32700:
        ESRI_FONTS_TO_QGIS_MARKERS['ESRI AMFM Sewer'].update({
            107: {'ellipse_marker_type': 'hexagon',
                  'width_factor': 0.299016444,
                  'height_factor': 0.25790167,
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
        },
        'ESRI NIMA VMAP1&2 LN': {
            35: {'font_name': 'ESRI NIMA City Graphic PT',
                 'character': 37},
        },
        'ESRI NIMA VMAP1&2 PT': {
            35: {'font_name': 'ESRI NIMA City Graphic PT',
                 'character': 37},
        },
        'ESRI SDS 2.00 1': {
            249: {'font_name': 'ESRI SDS 1.95 1',
                  'character': 249},
            196: {'font_name': 'ESRI SDS 1.95 1',
                  'character': 196},
            172: {'font_name': 'ESRI SDS 1.95 1',
                  'character': 172},
            171: {'font_name': 'ESRI SDS 1.95 1',
                  'character': 171},
            168: {'font_name': 'ESRI SDS 1.95 1',
                  'character': 168},
            167: {'font_name': 'ESRI SDS 1.95 1',
                  'character': 167},
            166: {'font_name': 'ESRI SDS 1.95 1',
                  'character': 166},
            161: {'font_name': 'ESRI SDS 1.95 1',
                  'character': 161},
            125: {'font_name': 'ESRI SDS 1.95 1',
                  'character': 125},
            124: {'font_name': 'ESRI SDS 1.95 1',
                  'character': 124},
            123: {'font_name': 'ESRI SDS 1.95 1',
                  'character': 123},
            121: {'font_name': 'ESRI SDS 1.95 1',
                  'character': 121},
            120: {'font_name': 'ESRI SDS 1.95 1',
                  'character': 120},
            119: {'font_name': 'ESRI SDS 1.95 1',
                  'character': 119},
            118: {'font_name': 'ESRI SDS 1.95 1',
                  'character': 118},
            117: {'font_name': 'ESRI SDS 1.95 1',
                  'character': 117},
            105: {'font_name': 'ESRI SDS 1.95 1',
                  'character': 105},
            104: {'font_name': 'ESRI SDS 1.95 1',
                  'character': 104},
            62: {'font_name': 'ESRI SDS 1.95 1',
                 'character': 62},
            61: {'font_name': 'ESRI SDS 1.95 1',
                 'character': 61},
        },
        'ESRI SDS 2.00 2': {
            220: {'font_name': 'ESRI SDS 1.95 2',
                  'character': 220},
            210: {'font_name': 'ESRI SDS 1.95 2',
                  'character': 220},
            209: {'font_name': 'ESRI SDS 1.95 2',
                  'character': 209},
            206: {'font_name': 'ESRI SDS 1.95 2',
                  'character': 206},
            205: {'font_name': 'ESRI SDS 1.95 2',
                  'character': 205},
            204: {'font_name': 'ESRI SDS 1.95 2',
                  'character': 204},
            203: {'font_name': 'ESRI SDS 1.95 2',
                  'character': 203},
            202: {'font_name': 'ESRI SDS 1.95 2',
                  'character': 202},
            198: {'font_name': 'ESRI SDS 1.95 2',
                  'character': 198},
            186: {'font_name': 'ESRI SDS 1.95 2',
                  'character': 186},
            185: {'font_name': 'ESRI SDS 1.95 2',
                  'character': 185},
            174: {'font_name': 'ESRI SDS 1.95 2',
                  'character': 174},
            44: {'font_name': 'ESRI SDS 1.95 2',
                 'character': 44},
            43: {'font_name': 'ESRI SDS 1.95 2',
                 'character': 43},
            39: {'font_name': 'ESRI SDS 1.95 2',
                 'character': 39},
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
    def can_convert_esri_font_character_to_simple_marker(font_name: str,
                                                         character: int) -> bool:
        """
        Returns True if a font marker with the specified name and character can be converted to a simple marker
        """
        if font_name in SymbolConverter.ALIAS_FONTS and character in \
                SymbolConverter.ALIAS_FONTS[font_name]:
            alias = SymbolConverter.ALIAS_FONTS[font_name][character]
            font_name = alias['font_name']
            character = alias['character']

        return character in SymbolConverter.ESRI_FONTS_TO_QGIS_MARKERS.get(
            font_name, {})

    @staticmethod
    def replace_char_if_needed(font_name: str, character: int) -> Tuple[
        str, int]:
        """
        Replaces font name and unicode using REPLACE_FONTS
        """
        if font_name in SymbolConverter.REPLACE_FONTS:
            if character in SymbolConverter.REPLACE_FONTS[font_name]:
                conversion = SymbolConverter.REPLACE_FONTS[font_name][
                    character]
                font_name = conversion['font_name']
                character = conversion['unicode']
        return font_name, character

    @staticmethod
    def append_CharacterMarkerSymbolLayer(symbol, layer: CharacterMarkerSymbol,
                                          context: Context):
        """
        Appends a CharacterMarkerSymbolLayer to a symbol
        """
        if isinstance(layer, CharacterMarkerSymbol):
            font, unicode = SymbolConverter.replace_char_if_needed(layer.font,
                                                                   layer.unicode)
        else:
            pass

        if context.convert_esri_fonts_to_simple_markers and SymbolConverter.can_convert_esri_font_character_to_simple_marker(
                font, unicode):
            SymbolConverter.append_CharacterMarkerSymbolLayerAsSimpleMarker(
                symbol, layer, context)
        elif context.convert_fonts:
            SymbolConverter.append_CharacterMarkerSymbolLayerAsSvg(symbol,
                                                                   layer,
                                                                   context)
        else:
            SymbolConverter.append_CharacterMarkerSymbolLayerAsFont(symbol,
                                                                    layer,
                                                                    context)

    @staticmethod
    def append_CharacterMarker3DSymbolLayer(symbol,
                                            layer: CharacterMarker3DSymbol,
                                            context: Context):
        """
        Appends a CharacterMarker3DSymbol  to a symbol
        """
        context.push_warning(
            '3D character marker was converted to a 2d character marker'
        )

        if context.convert_fonts:
            SymbolConverter.append_CharacterMarkerSymbolLayerAsSvg(symbol,
                                                                   layer.character_marker_symbol,
                                                                   context)
        else:
            SymbolConverter.append_CharacterMarkerSymbolLayerAsFont(symbol,
                                                                    layer.character_marker_symbol,
                                                                    context)

    @staticmethod
    def append_CharacterMarkerSymbolLayerAsSimpleMarker(symbol,
                                                        # pylint: disable=too-many-locals,too-many-statements,too-many-branches
                                                        layer: CharacterMarkerSymbol,
                                                        context: Context):
        """
        Appends a CharacterMarkerSymbolLayer to a symbol, converting the symbol to a simple qgis marker
        """
        if isinstance(layer, CharacterMarkerSymbol):
            font_name, character = SymbolConverter.replace_char_if_needed(
                layer.font, layer.unicode)
        else:
            pass

        vertical_offset_factor = 0
        if font_name in SymbolConverter.ALIAS_FONTS and character in \
                SymbolConverter.ALIAS_FONTS[font_name]:
            alias = SymbolConverter.ALIAS_FONTS[font_name][character]
            font_name = alias['font_name']
            character = alias['character']
            vertical_offset_factor = alias.get('vertical_offset_factor', 0)

        conversion_properties = \
        SymbolConverter.ESRI_FONTS_TO_QGIS_MARKERS[font_name][character]
        if conversion_properties is None:
            if symbol.symbolLayerCount():
                # don't add an empty shell
                return

            # add an effectively "null" symbol
            out = QgsSimpleMarkerSymbolLayer(
                QgsSimpleMarkerSymbolLayerBase.Circle, 8)
            out.setColor(QColor(255, 255, 255, 0))
            out.setStrokeStyle(Qt.NoPen)
            out.setLocked(True)
            out.setEnabled(layer.enabled)
            symbol.appendSymbolLayer(out)
            context.symbol_layer_output_to_input_index_map[
                out] = context.current_symbol_layer
            return

        if not vertical_offset_factor:
            vertical_offset_factor = conversion_properties.get(
                'vertical_offset_factor', 0)
        horizontal_offset_factor = conversion_properties.get(
            'horizontal_offset_factor', 0)

        if isinstance(layer, CharacterMarkerSymbol):
            color = ColorConverter.color_to_qcolor(layer.color)
        else:
            pass

        angle_offset = 0
        outline_stroke_width = 1
        size_scale_factor = 1
        if 'shape' in conversion_properties:
            marker_type = conversion_properties.get('shape',
                                                    QgsSimpleMarkerSymbolLayerBase.Square)

            if marker_type in (QgsSimpleMarkerSymbolLayerBase.Circle,
                               QgsSimpleMarkerSymbolLayerBase.Square,
                               QgsSimpleMarkerSymbolLayerBase.Diamond,
                               QgsSimpleMarkerSymbolLayerBase.EquilateralTriangle,
                               QgsSimpleMarkerSymbolLayerBase.Pentagon,
                               QgsSimpleMarkerSymbolLayerBase.Line,
                               QgsSimpleMarkerSymbolLayerBase.Cross,
                               QgsSimpleMarkerSymbolLayerBase.CrossFill,
                               QgsSimpleMarkerSymbolLayerBase.Cross2):
                simple_size = (1.47272 * layer.size) / 2.0
            elif marker_type == QgsSimpleMarkerSymbolLayerBase.Hexagon:
                simple_size = (
                                          1.47272 * layer.size * 4.178160 / 4.418160) / 2.0
            elif marker_type == QgsSimpleMarkerSymbolLayerBase.Star:
                simple_size = (
                                          1.47272 * layer.size * 12.327200 / 14.727200) / 2.0
            elif marker_type == QgsSimpleMarkerSymbolLayerBase.SemiCircle:
                simple_size = (
                                          1.47272 * layer.size * 12.327200 / 14.727200) / 2.0
            elif Qgis.QGIS_VERSION_INT >= 31800:
                if marker_type in (QgsSimpleMarkerSymbolLayerBase.Octagon,
                                   QgsSimpleMarkerSymbolLayerBase.SquareWithCorners):
                    simple_size = (1.3632460 * layer.size) / 2.0
                elif marker_type == QgsSimpleMarkerSymbolLayerBase.AsteriskFill:
                    simple_size = (1.3632460 * layer.size) / 2.0

            try:
                simple_size *= conversion_properties.get('shape_size_factor', 1)
            except NameError as e:
                if "simple_size" in str(e):
                    raise NotImplementedException(f"Unknown size multipyer for {marker_type}.") from e
                raise e

            stroke_only_symbol = not QgsSimpleMarkerSymbolLayerBase.shapeIsFilled(
                marker_type) or conversion_properties.get('outline_only',
                                                          False)

            out = None
            if False:  # pylint: disable=using-constant-test
                pass

            if out is None:
                out = QgsSimpleMarkerSymbolLayer(marker_type,
                                                 context.convert_size(
                                                     simple_size))

            y_offset = (
                                   layer.y_offset or 0) + vertical_offset_factor * simple_size
            x_offset = (
                                   layer.x_offset or 0) + horizontal_offset_factor * simple_size

            SHAPE_BASED_OFFSET = {
                QgsSimpleMarkerSymbolLayerBase.EquilateralTriangle: 1.8 / 14.7272,
                QgsSimpleMarkerSymbolLayerBase.Pentagon: 0.2 / 4.418160,
                QgsSimpleMarkerSymbolLayerBase.Star: 0.600000 / 12.327200
            }

            if 'cap_style' in conversion_properties:
                try:
                    out.setPenCapStyle(conversion_properties['cap_style'])
                except AttributeError:
                    pass

            if marker_type in SHAPE_BASED_OFFSET:
                y_offset -= simple_size * SHAPE_BASED_OFFSET[marker_type]

            if marker_type == QgsSimpleMarkerSymbolLayerBase.Hexagon:
                angle_offset += 90

            if 'angle' in conversion_properties:
                angle_offset += conversion_properties['angle']

            if marker_type == QgsSimpleMarkerSymbolLayerBase.Star:
                outline_stroke_width = (layer.size / 48) * 1.016667 / 0.416667
            else:
                outline_stroke_width = layer.size / 48

            outline_stroke_width *= conversion_properties.get(
                'stroke_size_factor', 1)

            if marker_type != QgsSimpleMarkerSymbolLayerBase.Star:
                size_scale_factor = 10.781760 / 11.781760

        elif 'ellipse_marker_type' in conversion_properties:
            symbol_name = conversion_properties['ellipse_marker_type']

            simple_size = (1.47272 * layer.size) / 2.0

            out = QgsEllipseSymbolLayer()
            out.setSymbolName(symbol_name)
            out.setSymbolWidth(
                simple_size * conversion_properties.get('width_factor', 1))
            out.setSymbolHeight(
                simple_size * conversion_properties.get('height_factor', 1))

            stroke_only_symbol = conversion_properties.get('outline_only',
                                                           False)
            x_offset = (
                                   layer.x_offset or 0) + horizontal_offset_factor * simple_size
            y_offset = (
                                   layer.y_offset or 0) + vertical_offset_factor * simple_size
            outline_stroke_width = layer.size / 24

            outline_stroke_width *= conversion_properties.get('stroke_scale',
                                                              1)

            if 'angle' in conversion_properties:
                angle_offset += conversion_properties['angle']

        out.setSizeUnit(context.units)

        if isinstance(out,
                      (QgsSimpleMarkerSymbolLayer, QgsEllipseSymbolLayer)):
            out.setPenJoinStyle(Qt.MiterJoin)

        out.setEnabled(layer.enabled)
        out.setLocked(layer.locked or character == 32)
        if isinstance(layer, CharacterMarkerSymbol):
            if layer.symbol_level != 0xffffffff:
                out.setRenderingPass(layer.symbol_level)

        if isinstance(layer, CharacterMarkerSymbol):
            angle = ConversionUtils.convert_angle(layer.angle)
        else:
            if layer.rotation:
                if layer.rotate_clockwise:
                    angle = layer.rotation
                else:
                    angle = -layer.rotation
            else:
                angle = 0

        angle += angle_offset
        out.setAngle(angle)

        offset_x = context.convert_size(x_offset)
        offset_y = -context.convert_size(y_offset)

        if False:  # pylint: disable=using-constant-test
            pass

        if False:  # pylint: disable=using-constant-test
            pass
        else:
            out.setOffset(
                # ConversionUtils.adjust_offset_for_rotation(
                QPointF(offset_x, offset_y))
            #    angle))

        out.setOffsetUnit(context.units)

        if not stroke_only_symbol and isinstance(out, (
        QgsSimpleMarkerSymbolLayer, QgsEllipseSymbolLayer)):
            out.setStrokeStyle(Qt.NoPen)

        appended_to_prev_layer = False

        if False:  # pylint: disable=using-constant-test
            pass
        if not stroke_only_symbol and isinstance(out, (
        QgsSimpleMarkerSymbolLayer, QgsEllipseSymbolLayer)):
            out.setColor(color)
        else:
            if symbol.symbolLayerCount() > 0:
                prev_layer = symbol.symbolLayer(symbol.symbolLayerCount() - 1)
                prev_converted_layer = context.current_symbol.layers[
                    context.current_symbol_layer - 1] if context.current_symbol_layer else None

                # in ESRI land people often place outline only versions of font markers over the filled
                # versions in order to get an outline

                can_condense_to_simple_marker = prev_converted_layer is not None and \
                                                isinstance(out,
                                                           QgsSimpleMarkerSymbolLayer) and \
                                                isinstance(prev_layer,
                                                           QgsSimpleMarkerSymbolLayer) and \
                                                out.type() == prev_layer.type() and \
                                                prev_converted_layer.size == layer.size and prev_layer.angle() == out.angle() and \
                                                prev_layer.offset() == out.offset() and prev_layer.strokeStyle() == Qt.NoPen

                can_condense_to_ellipse_marker = prev_converted_layer is not None and \
                                                 isinstance(out,
                                                            QgsEllipseSymbolLayer) and \
                                                 isinstance(prev_layer,
                                                            QgsEllipseSymbolLayer) and \
                                                 out.symbolName() == prev_layer.symbolName() and \
                                                 prev_converted_layer.size == layer.size and \
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
                    prev_layer.setStrokeWidth(context.convert_size(
                        context.fix_line_width(layer.size / 48)))
                    prev_layer.setStrokeWidthUnit(context.units)
                elif can_condense_to_ellipse_marker:
                    # effectively the same symbol, just an outline version of it! Let's make the results nice
                    # and QGIS-esque by just adding the stroke to the previous layer instead of creating a brand
                    # new layer
                    appended_to_prev_layer = True
                    prev_layer.setStrokeStyle(Qt.SolidLine)
                    prev_layer.setStrokeColor(color)
                    prev_layer.setStrokeWidth(context.convert_size(
                        context.fix_line_width(layer.size / 24)))
                    prev_layer.setStrokeWidthUnit(context.units)

            if not appended_to_prev_layer:
                out.setStrokeColor(color)

        if not appended_to_prev_layer and conversion_properties.get(
                'outline_only', False):
            if not isinstance(out,
                              QgsSimpleMarkerSymbolLayerBase) or QgsSimpleMarkerSymbolLayerBase.shapeIsFilled(
                    out.shape()):
                out.setColor(QColor(255, 255, 255, 0))
            out.setStrokeWidth(context.convert_size(
                context.fix_line_width(outline_stroke_width)))
            out.setStrokeWidthUnit(context.units)
            out.setSize(out.size() * size_scale_factor)

        if not appended_to_prev_layer:

            if False:  # pylint: disable=using-constant-test
                pass
            else:
                symbol.appendSymbolLayer(out)
                context.symbol_layer_output_to_input_index_map[
                    out] = context.current_symbol_layer

        if 'overlay' in conversion_properties:
            # Add overlay layer
            marker_type = conversion_properties['overlay']

            overlay_size = out.size() * conversion_properties.get(
                'overlay_size_factor', 1)

            overlay = QgsSimpleMarkerSymbolLayer(marker_type, overlay_size)
            overlay.setSizeUnit(context.units)

            stroke_only_symbol = not QgsSimpleMarkerSymbolLayerBase.shapeIsFilled(
                marker_type)

            if not stroke_only_symbol:
                overlay.setColor(color)
                out.setStrokeStyle(Qt.NoPen)
            else:
                overlay.setStrokeColor(color)

            if marker_type == QgsSimpleMarkerSymbolLayerBase.Star:
                overlay.setStrokeWidth(
                    context.convert_size(context.fix_line_width(
                        layer.size / 48 * 1.016667 / 0.416667)))
            else:
                overlay.setStrokeWidth(context.convert_size(
                    context.fix_line_width(layer.size / 48)))
            overlay.setStrokeWidthUnit(context.units)

            overlay.setEnabled(layer.enabled)
            overlay.setLocked(layer.locked or character == 32)
            if isinstance(layer, CharacterMarkerSymbol):
                if layer.symbol_level != 0xffffffff:
                    overlay.setRenderingPass(layer.symbol_level)

            if isinstance(layer, CharacterMarkerSymbol):
                angle = ConversionUtils.convert_angle(layer.angle)
            else:
                if layer.rotation:
                    if layer.rotate_clockwise:
                        angle = layer.rotation
                    else:
                        angle = -layer.rotation
                else:
                    angle = 0

            angle += conversion_properties.get('overlay_angle', 0)

            overlay.setAngle(angle)

            overlay.setOffset(
                ConversionUtils.adjust_offset_for_rotation(
                    QPointF(context.convert_size(layer.x_offset or 0),
                            -context.convert_size(y_offset)),
                    angle))

            overlay.setOffset(QPointF(overlay.offset().x(),
                                      overlay.offset().y() * conversion_properties.get(
                                          'overlay_y_offset_factor', 0)))

            overlay.setOffsetUnit(context.units)

            if False:  # pylint: disable=using-constant-test
                pass
            else:
                symbol.appendSymbolLayer(overlay)
                context.symbol_layer_output_to_input_index_map[
                    overlay] = context.current_symbol_layer

        if 'central_overlay' in conversion_properties:
            # Add central dot symbol layer
            marker_type = conversion_properties['central_overlay']

            simple_size = (1.47272 * layer.size) / 2.0
            if marker_type == QgsSimpleMarkerSymbolLayerBase.Circle:
                simple_size *= 2.901760 / 11.781760
            elif marker_type == QgsSimpleMarkerSymbolLayerBase.Square:
                simple_size *= 2.041760 / 11.781760

            simple_size *= conversion_properties.get('overlay_size_factor', 1)

            stroke_only_symbol = not QgsSimpleMarkerSymbolLayerBase.shapeIsFilled(
                marker_type) or conversion_properties.get(
                'central_overlay_outline_only', False)

            out = QgsSimpleMarkerSymbolLayer(marker_type,
                                             context.convert_size(simple_size))
            out.setSizeUnit(context.units)

            if not stroke_only_symbol:
                out.setColor(color)
                out.setStrokeStyle(Qt.NoPen)
            else:
                out.setColor(QColor(255, 255, 255, 0))
                out.setStrokeColor(color)
                out.setStrokeStyle(Qt.SolidLine)

                out.setStrokeWidth(context.convert_size(context.fix_line_width(
                    outline_stroke_width * conversion_properties.get(
                        'overlay_stroke_factor', 1))))
                out.setStrokeWidthUnit(context.units)

            out.setEnabled(layer.enabled)
            out.setLocked(layer.locked or character == 32)
            if isinstance(layer, CharacterMarkerSymbol):
                if layer.symbol_level != 0xffffffff:
                    out.setRenderingPass(layer.symbol_level)

            if isinstance(layer, CharacterMarkerSymbol):
                angle = ConversionUtils.convert_angle(layer.angle)
            else:
                pass

            angle += conversion_properties.get('overlay_angle', 0)

            out.setAngle(angle)

            out.setOffset(
                ConversionUtils.adjust_offset_for_rotation(
                    QPointF(context.convert_size(layer.x_offset or 0),
                            -context.convert_size(y_offset)),
                    angle))

            if 'overlay_y_offset' in conversion_properties:
                out.setOffset(QPointF(out.offset().x(),
                                      out.size() * conversion_properties[
                                          'overlay_y_offset']))

            out.setOffset(
                QPointF(out.offset().x(),
                        out.offset().y() * conversion_properties.get(
                            'overlay_y_offset_factor', 1)))

            out.setOffsetUnit(context.units)

            if False:  # pylint: disable=using-constant-test
                pass
            else:
                symbol.appendSymbolLayer(out)
                context.symbol_layer_output_to_input_index_map[
                    out] = context.current_symbol_layer

    # pylint: disable=too-many-locals,too-many-statements,too-many-branches
    @staticmethod
    def append_CharacterMarkerSymbolLayerAsSvg(symbol,
                                               layer: CharacterMarkerSymbol,
                                               context: Context):
        """
        Appends a CharacterMarkerSymbolLayer to a symbol, rendering the font character
        to an SVG file.
        """
        if isinstance(layer, CharacterMarkerSymbol):
            font_family, unicode = SymbolConverter.replace_char_if_needed(
                layer.font, layer.unicode)
        else:
            pass

        if font_family not in QFontDatabase().families():
            context.push_warning(
                'Font {} not available on system'.format(font_family)
            )

        character = chr(unicode)
        if isinstance(layer, CharacterMarkerSymbol):
            color = ColorConverter.color_to_qcolor(layer.color)
        else:
            pass

        if isinstance(layer, CharacterMarkerSymbol):
            original_angle = layer.angle
            angle = ConversionUtils.convert_angle(layer.angle)
        else:
            pass

        font = QFont(font_family)
        font.setPointSizeF(layer.size)

        # Using the rect of a painter path gives better results then using font metrics
        path = QPainterPath()
        path.setFillRule(Qt.WindingFill)
        path.addText(0, 0, font, character)

        rect = path.boundingRect()

        font_bounding_rect = QFontMetricsF(font).boundingRect(character)

        # adjust size -- marker size in esri is the font size, svg marker size in qgis is the svg rect size
        if isinstance(layer, CharacterMarkerSymbol):
            scale = rect.width() / font_bounding_rect.width() if font_bounding_rect.width() else 1
        else:
            scale = 1

        gen = QSvgGenerator()
        svg_path = SymbolConverter.symbol_name_to_filename(context.symbol_name,
                                                           context.get_picture_store_folder(),
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

        with open(svg_path, 'r', encoding='utf-8') as f:
            t = f.read()

        t = t.replace('#ff0000', 'param(fill)')
        t = t.replace('fill-opacity="1" ',
                      'fill-opacity="param(fill-opacity)"')
        t = t.replace('stroke="none"',
                      'stroke="param(outline)" stroke-opacity="param(outline-opacity) 1" stroke-width="param(outline-width) 0"')

        if context.embed_pictures:
            svg_content = base64.b64encode(t.encode('UTF-8')).decode('UTF-8')
            # no longer need the svg file
            try:
                os.remove(svg_path)
            except PermissionError:
                pass
            svg_path = 'base64:{}'.format(svg_content)
        else:
            with open(svg_path, 'w', encoding='utf8') as f:
                f.write(t)
            svg_path = context.convert_path(svg_path)

        out = QgsSvgMarkerSymbolLayer(svg_path)

        out.setSizeUnit(context.units)
        # esri symbol sizes are for height, QGIS are for width
        if isinstance(layer, CharacterMarkerSymbol):
            if out.defaultAspectRatio() != 1 and out.defaultAspectRatio() != 0:
                out.setSize(context.convert_size(
                    scale * rect.width()) / out.defaultAspectRatio())
            else:
                out.setSize(context.convert_size(scale * rect.width()))
        else:
            pass
        out.setAngle(angle)
        out.setFillColor(color)
        out.setStrokeWidth(0)

        out.setEnabled(layer.enabled)
        out.setLocked(layer.locked)
        if isinstance(layer, CharacterMarkerSymbol):
            if layer.symbol_level != 0xffffffff:
                out.setRenderingPass(layer.symbol_level)

        if False:  # pylint: disable=using-constant-test
            pass

        if False:  # pylint: disable=using-constant-test
            pass
        else:
            out.setOffset(
                ConversionUtils.adjust_offset_for_rotation(
                    QPointF(context.convert_size(layer.x_offset or 0),
                            -context.convert_size(layer.y_offset or 0)),
                    original_angle))
        out.setOffsetUnit(context.units)

        if False:  # pylint: disable=using-constant-test
            pass
        else:
            symbol.appendSymbolLayer(out)
            context.symbol_layer_output_to_input_index_map[
                out] = context.current_symbol_layer

    # pylint: enable=too-many-locals,too-many-statements,too-many-branches

    # pylint: disable=too-many-locals,too-many-branches
    @staticmethod
    def append_CharacterMarkerSymbolLayerAsFont(symbol,
                                                layer: CharacterMarkerSymbol,
                                                context: Context):
        """
        Appends a CharacterMarkerSymbolLayer to a symbol, using QGIS font marker symbols
        """
        if isinstance(layer, CharacterMarkerSymbol):
            font_family, unicode = SymbolConverter.replace_char_if_needed(
                layer.font, layer.unicode)
        else:
            pass

        if font_family not in QFontDatabase().families():
            context.push_warning(
                'Font {} not available on system'.format(font_family)
            )

        character = chr(unicode)

        if isinstance(layer, CharacterMarkerSymbol):
            color = ColorConverter.color_to_qcolor(layer.color)
        else:
            pass

        # we need to calculate the character bounding box, as ESRI font marker symbols are rendered centered
        # on the character's bounding box (not the overall font metrics, like QGIS does)
        font = QFont(font_family)
        font.setPointSizeF(layer.size)
        font_metrics = QFontMetricsF(font)

        # This seems to give best conversion match to ESRI - vs tightBoundingRect
        rect = font_metrics.boundingRect(character)
        # note the font_metrics.width/ascent adjustments are here to reverse how QGIS offsets font markers
        x_offset_points = rect.center().x() - font_metrics.width(
            character) / 2.0
        y_offset_points = -rect.center().y() - font_metrics.ascent() / 2.0

        if isinstance(layer, CharacterMarkerSymbol):
            original_angle = layer.angle
            angle = ConversionUtils.convert_angle(layer.angle)
        else:
            pass

        out = QgsFontMarkerSymbolLayer(font_family, character,
                                       context.convert_size(layer.size), color,
                                       angle)
        out.setSizeUnit(context.units)

        out.setEnabled(layer.enabled)
        out.setLocked(layer.locked)
        if isinstance(layer, CharacterMarkerSymbol):
            if layer.symbol_level != 0xffffffff:
                out.setRenderingPass(layer.symbol_level)

        if False:  # pylint: disable=using-constant-test
            pass

        offset_x = layer.x_offset or 0
        offset_y = layer.y_offset or 0
        if False:  # pylint: disable=using-constant-test
            pass

        temp_offset = ConversionUtils.adjust_offset_for_rotation(
            QPointF(offset_x, -offset_y), original_angle)
        out.setOffset(
            QPointF(context.convert_size(temp_offset.x() + x_offset_points),
                    context.convert_size(temp_offset.y() + y_offset_points)))

        out.setOffsetUnit(context.units)

        if False:  # pylint: disable=using-constant-test
            pass
        else:
            symbol.appendSymbolLayer(out)
            context.symbol_layer_output_to_input_index_map[
                out] = context.current_symbol_layer

    # pylint: enable=too-many-locals,too-many-branches

    # pylint: disable=too-many-branches,too-many-statements
    @staticmethod
    def append_PictureMarkerSymbolLayer(symbol,
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
                issubclass(picture.__class__,
                           BmpPicture) and picture.format == BmpPicture.FORMAT_EMF) \
                or Qgis.QGIS_VERSION_INT < 30600:
            if issubclass(picture.__class__, EmfPicture) or (
                    issubclass(picture.__class__,
                               BmpPicture) and picture.format == BmpPicture.FORMAT_EMF):
                path = SymbolConverter.symbol_name_to_filename(
                    context.symbol_name, context.get_picture_store_folder(),
                    'emf')
                with open(path, 'wb') as f:
                    f.write(picture.content)

                svg_path = SymbolConverter.symbol_name_to_filename(
                    context.symbol_name,
                    context.get_picture_store_folder(), 'svg')
                SymbolConverter.emf_to_svg(path, svg_path,
                                           inkscape_path=context.inkscape_path,
                                           context=context)
                # no longer need the emf file
                try:
                    os.remove(path)
                except PermissionError:
                    pass

                if not os.path.exists(svg_path):
                    context.push_warning(
                        'Conversion of EMF picture failed',
                        level=Context.CRITICAL)

                if context.embed_pictures and os.path.exists(svg_path):
                    with open(svg_path, 'rb') as svg_file:
                        svg_content = base64.b64encode(svg_file.read()).decode(
                            'UTF-8')
                    # no longer need the svg file
                    try:
                        os.remove(svg_path)
                    except PermissionError:
                        pass
                    svg_path = 'base64:{}'.format(svg_content)
                else:
                    svg_path = context.convert_path(svg_path)
            else:
                svg = PictureUtils.to_embedded_svg(picture.content,
                                                   ColorConverter.color_to_qcolor(
                                                       layer.color_foreground),
                                                   ColorConverter.color_to_qcolor(
                                                       layer.color_background),
                                                   ColorConverter.color_to_qcolor(
                                                       layer.color_transparent))
                if context.embed_pictures:
                    svg_base64 = base64.b64encode(svg.encode('UTF-8')).decode(
                        'UTF-8')
                    svg_path = 'base64:{}'.format(svg_base64)
                else:
                    svg_path = SymbolConverter.write_svg(svg,
                                                         context.symbol_name,
                                                         context.get_picture_store_folder())
                    svg_path = context.convert_path(svg_path)

            out = QgsSvgMarkerSymbolLayer(svg_path,
                                          context.convert_size(layer.size),
                                          layer.angle)

            # esri symbol sizes are for height, QGIS are for width
            if out.defaultAspectRatio() != 1 and out.defaultAspectRatio() != 0:
                out.setSize(context.convert_size(
                    layer.size) / out.defaultAspectRatio())

        else:
            if context.embed_pictures:
                picture_data = SymbolConverter.get_picture_data(picture,
                                                                layer.color_foreground,
                                                                layer.color_background,
                                                                layer.color_transparent,
                                                                context=context)
                image_base64 = base64.b64encode(picture_data).decode('UTF-8')
                image_path = 'base64:{}'.format(image_base64)
            else:
                image_path = SymbolConverter.write_picture(picture,
                                                           context.symbol_name,
                                                           context.get_picture_store_folder(),
                                                           layer.color_foreground,
                                                           layer.color_background,
                                                           layer.color_transparent,
                                                           context=context)
            # unsure -- should this angle be converted? probably!
            out = QgsRasterMarkerSymbolLayer(image_path,
                                             context.convert_size(layer.size),
                                             layer.angle)

        out.setSizeUnit(context.units)
        out.setEnabled(layer.enabled)
        out.setLocked(layer.locked)
        if layer.symbol_level != 0xffffffff:
            out.setRenderingPass(layer.symbol_level)
        out.setOffset(
            ConversionUtils.adjust_offset_for_rotation(
                QPointF(context.convert_size(layer.x_offset),
                        -context.convert_size(layer.y_offset)),
                layer.angle))
        out.setOffsetUnit(context.units)

        symbol.appendSymbolLayer(out)
        context.symbol_layer_output_to_input_index_map[
            out] = context.current_symbol_layer

    # pylint: enable=too-many-branches,too-many-statements

    @staticmethod
    def reverse_line_symbol(symbol: QgsLineSymbol) -> QgsLineSymbol:
        """
        Reverses a line symbol, eg placing start vertex markers at the end
        """
        res = symbol.clone()
        for i in range(res.symbolLayerCount()):
            layer = res.symbolLayer(i)
            if isinstance(layer, QgsMarkerLineSymbolLayer):
                if layer.placement() == QgsMarkerLineSymbolLayer.FirstVertex:
                    layer.setPlacement(QgsMarkerLineSymbolLayer.LastVertex)
                elif layer.placement() == QgsMarkerLineSymbolLayer.LastVertex:
                    layer.setPlacement(QgsMarkerLineSymbolLayer.FirstVertex)

            # TODO - other symbol layer types?

        return res

    class SymbolLayerCapability(Enum):
        """
        Symbol layer capabilities
        """
        FillOffset = 1
        LineOffset = 2
        LineCut = 4
        LineDashes = 8

    @staticmethod
    def symbol_layer_capabilities(layer):  # pylint: disable=too-many-return-statements
        """
        Returns symbol layer capabilities
        """
        if isinstance(layer, QgsCentroidFillSymbolLayer):
            return 0
        elif isinstance(layer, QgsGradientFillSymbolLayer):
            return SymbolConverter.SymbolLayerCapability.FillOffset.value
        elif isinstance(layer, QgsLinePatternFillSymbolLayer):
            return 0
        elif isinstance(layer, QgsPointPatternFillSymbolLayer):
            return 0
        elif isinstance(layer, QgsRasterFillSymbolLayer):
            return SymbolConverter.SymbolLayerCapability.FillOffset.value
        elif isinstance(layer, QgsSVGFillSymbolLayer):
            return 0
        elif isinstance(layer, QgsShapeburstFillSymbolLayer):
            return SymbolConverter.SymbolLayerCapability.FillOffset.value
        elif isinstance(layer, QgsSimpleFillSymbolLayer):
            return SymbolConverter.SymbolLayerCapability.FillOffset.value | SymbolConverter.SymbolLayerCapability.LineDashes.value
        elif isinstance(layer, QgsSimpleLineSymbolLayer):
            return SymbolConverter.SymbolLayerCapability.LineOffset.value | SymbolConverter.SymbolLayerCapability.LineCut.value | SymbolConverter.SymbolLayerCapability.LineDashes.value

        if Qgis.QGIS_VERSION_INT >= 31100:
            from qgis.core import \
                QgsRandomMarkerFillSymbolLayer  # pylint: disable=import-outside-toplevel
            if isinstance(layer, QgsRandomMarkerFillSymbolLayer):
                return 0

        return 0
