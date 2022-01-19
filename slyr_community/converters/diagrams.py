#!/usr/bin/env python

# /***************************************************************************
# diagrams.py
# ----------
# Date                 : November 2019
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
Diagram conversion
"""

from qgis.PyQt.QtCore import QSizeF
from qgis.core import (
    QgsDiagramLayerSettings,
    QgsHistogramDiagram,
    QgsDiagramSettings,
    QgsLinearlyInterpolatedDiagramRenderer,
    QgsSingleCategoryDiagramRenderer,
    QgsVectorLayer,
    QgsPieDiagram,
    QgsProperty
)

from .context import Context
from .symbols import SymbolConverter
from ..parser.exceptions import NotImplementedException
from ..parser.objects.annotate_layer_properties_collection import AnnotateLayerPropertiesCollection
from ..parser.objects.bar_chart_symbol import BarChartSymbol
from ..parser.objects.chart_renderer import ChartRenderer
from ..parser.objects.pie_chart_symbol import PieChartSymbol


class DiagramConverter:
    """
    Converts diagram symbols
    """

    @staticmethod
    def convert_diagrams(renderer: AnnotateLayerPropertiesCollection,  # pylint: disable=too-many-branches,too-many-statements
                         dest_layer: QgsVectorLayer,
                         context):
        """
        Converts a diagram renderer to QGIS diagrams
        """
        if not isinstance(renderer, ChartRenderer):
            return

        layer_settings = QgsDiagramLayerSettings()
        # todo - geometry type dependent
        layer_settings.placement = QgsDiagramLayerSettings.OverPoint

        if not renderer.prevent_overlap:
            layer_settings.setShowAllDiagrams(True)

        settings = QgsDiagramSettings()
        settings.categoryLabels = renderer.labels
        settings.categoryAttributes = renderer.attributes
        settings.categoryColors = [SymbolConverter.symbol_to_color(c.symbol, context) for c in
                                   renderer.class_legend.classes]

        if isinstance(renderer.symbol, BarChartSymbol):
            if renderer.symbol.display_in_3d and context.unsupported_object_callback:
                if context.layer_name:
                    context.unsupported_object_callback(
                        '{}: 3D bar chart was converted to 2d (QGIS does not support 3D bar charts)'.format(
                            context.layer_name),
                        level=Context.WARNING)
                elif context.symbol_name:
                    context.unsupported_object_callback(
                        '{}: 3D bar chart was converted to 2d (QGIS does not support 3D bar charts)'.format(
                            context.symbol_name), level=Context.WARNING)
                else:
                    context.unsupported_object_callback(
                        '3D bar chart was converted to 2d (QGIS does not support 3D bar charts)', level=Context.WARNING)

            if renderer.class_legend.classes:
                first_symbol = renderer.class_legend.classes[0].symbol
                settings.penColor = SymbolConverter.symbol_to_line_color(first_symbol, context)
                settings.penWidth = SymbolConverter.symbol_to_line_width(first_symbol, context)
                settings.lineSizeUnit = context.units

            try:
                axis_symbol = SymbolConverter.Symbol_to_QgsSymbol(renderer.symbol.axis_symbol, context)
                settings.setShowAxis(renderer.symbol.show_axis)
                settings.setAxisLineSymbol(axis_symbol)
            except AttributeError:
                if context.unsupported_object_callback:
                    if context.layer_name:
                        context.unsupported_object_callback(
                            '{}: Bar chart axis symbols require QGIS 3.12 or later'.format(
                                context.layer_name),
                            level=Context.WARNING)
                    elif context.symbol_name:
                        context.unsupported_object_callback(
                            '{}: Bar chart axis symbols require QGIS 3.12 or later'.format(
                                context.symbol_name), level=Context.WARNING)
                    else:
                        context.unsupported_object_callback(
                            'Bar chart axis symbols require QGIS 3.12 or later', level=Context.WARNING)

            settings.barWidth = renderer.symbol.bar_width * 0.352778

            if renderer.symbol.spacing:
                try:
                    settings.setSpacing(context.convert_size(renderer.symbol.spacing))
                    settings.setSpacingUnit(context.units)
                except AttributeError:
                    if context.unsupported_object_callback:
                        if context.layer_name:
                            context.unsupported_object_callback(
                                '{}: Bar chart spacing requires QGIS 3.12 or later'.format(
                                    context.layer_name),
                                level=Context.WARNING)
                    elif context.symbol_name:
                        context.unsupported_object_callback(
                            '{}: Bar chart spacing requires QGIS 3.12 or later'.format(
                                context.symbol_name), level=Context.WARNING)
                    else:
                        context.unsupported_object_callback(
                            'Bar chart spacing requires QGIS 3.12 or later', level=Context.WARNING)

            if not renderer.symbol.orientation_vertical:
                settings.diagramOrientation = QgsDiagramSettings.Right

            diagram_renderer = QgsLinearlyInterpolatedDiagramRenderer()
            diagram_renderer.setDiagram(QgsHistogramDiagram())
            diagram_renderer.setUpperValue(renderer.symbol.max_value)
            diagram_renderer.setUpperSize(
                QSizeF(renderer.symbol.max_length * 0.352778, renderer.symbol.max_length * 0.352778))
            diagram_renderer.setDiagramSettings(settings)

            dest_layer.setDiagramRenderer(diagram_renderer)
            dest_layer.setDiagramLayerSettings(layer_settings)
        elif isinstance(renderer.symbol, PieChartSymbol):
            if renderer.symbol.display_in_3d and context.unsupported_object_callback:
                if context.layer_name:
                    context.unsupported_object_callback(
                        '{}: 3D pie chart was converted to 2d (QGIS does not support 3D pie charts)'.format(
                            context.layer_name),
                        level=Context.WARNING)
                elif context.symbol_name:
                    context.unsupported_object_callback(
                        '{}: 3D pie chart was converted to 2d (QGIS does not support 3D pie charts)'.format(
                            context.symbol_name), level=Context.WARNING)
                else:
                    context.unsupported_object_callback(
                        '3D pie chart was converted to 2d (QGIS does not support 3D pie charts)', level=Context.WARNING)

            outline = SymbolConverter.Symbol_to_QgsSymbol(renderer.symbol.outline, context)
            settings.penWidth = outline.width() * 0.352778
            settings.penColor = outline.color()

            # ArcMap only shows pie charts for features with some non-zero attributes
            exp = ' or '.join(settings.categoryAttributes)
            layer_settings.dataDefinedProperties().setProperty(QgsDiagramLayerSettings.Show,
                                                               QgsProperty.fromExpression(exp))

            if not renderer.vary_size_by_attribute:
                diagram_renderer = QgsSingleCategoryDiagramRenderer()
            else:
                diagram_renderer = QgsLinearlyInterpolatedDiagramRenderer()
                diagram_renderer.setClassificationField(renderer.vary_size_by_attribute)
                diagram_renderer.setLowerValue(renderer.min_value)
                diagram_renderer.setLowerSize(
                    QSizeF(renderer.min_size * 0.352778 * 0.5, renderer.min_size * 0.352778 * 0.5))
                diagram_renderer.setUpperValue(renderer.min_value * 2)
                diagram_renderer.setUpperSize(
                    QSizeF(renderer.min_size * 0.352778 * 2 * 0.5, renderer.min_size * 0.352778 * 2 * 0.5))
                settings.scaleByArea = False
            diagram_renderer.setDiagram(QgsPieDiagram())
            settings.size = QSizeF(context.convert_size(renderer.symbol.size),
                                   context.convert_size(renderer.symbol.size))
            settings.sizeType = context.units

            if renderer.symbol.clockwise:
                try:
                    settings.setDirection(QgsDiagramSettings.Clockwise)
                except AttributeError:
                    if context.unsupported_object_callback:
                        if context.layer_name:
                            context.unsupported_object_callback(
                                '{}: Clockwise pie charts require QGIS 3.12 or later'.format(
                                    context.layer_name),
                                level=Context.WARNING)
                    elif context.symbol_name:
                        context.unsupported_object_callback(
                            '{}: Clockwise pie charts require QGIS 3.12 or later'.format(
                                context.symbol_name), level=Context.WARNING)
                    else:
                        context.unsupported_object_callback(
                            'Clockwise pie charts require QGIS 3.12 or later', level=Context.WARNING)

            try:
                outline_symbol = SymbolConverter.Symbol_to_QgsSymbol(renderer.class_legend.classes[0].symbol.outline,
                                                                     context).color()
                if outline_symbol:
                    settings.penColor = outline_symbol.color()
                    settings.penWidth = outline_symbol.width() * 0.352778

            except AttributeError:
                pass

            if not renderer.symbol.clockwise:
                settings.rotationOffset = renderer.symbol.starting_angle
            else:
                settings.rotationOffset = 360.0 - renderer.symbol.starting_angle

            diagram_renderer.setDiagramSettings(settings)

            dest_layer.setDiagramRenderer(diagram_renderer)
            dest_layer.setDiagramLayerSettings(layer_settings)

        else:
            raise NotImplementedException(
                'Converting {} diagrams is not yet supported'.format(renderer.symbol.__class__.__name__))
