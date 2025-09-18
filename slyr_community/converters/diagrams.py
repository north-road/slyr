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
from qgis.PyQt.QtGui import QColor
from qgis.core import (
    Qgis,
    QgsDiagramLayerSettings,
    QgsHistogramDiagram,
    QgsDiagramSettings,
    QgsLinearlyInterpolatedDiagramRenderer,
    QgsSingleCategoryDiagramRenderer,
    QgsVectorLayer,
    QgsPieDiagram,
    QgsProperty,
    QgsExpression,
)

from .context import Context
from .symbols import SymbolConverter
from ..parser.exceptions import NotImplementedException
from ..parser.objects.bar_chart_symbol import BarChartSymbol
from ..parser.objects.chart_renderer import ChartRenderer
from ..parser.objects.pie_chart_symbol import PieChartSymbol
from ..parser.objects.stacked_chart_symbol import StackedChartSymbol


class DiagramConverter:
    """
    Converts diagram symbols
    """

    # pylint: disable=too-many-branches,too-many-statements
    @staticmethod
    def convert_diagrams(renderer: ChartRenderer, dest_layer: QgsVectorLayer, context):
        """
        Converts a diagram renderer to QGIS diagrams
        """
        if not isinstance(renderer, (ChartRenderer,)):
            return

        layer_settings = QgsDiagramLayerSettings()
        # todo - geometry type dependent
        layer_settings.placement = QgsDiagramLayerSettings.OverPoint

        if not renderer.prevent_overlap:
            layer_settings.setShowAllDiagrams(True)

        settings = QgsDiagramSettings()
        settings.categoryLabels = renderer.labels
        settings.categoryAttributes = renderer.attributes
        if True:  # pylint: disable=using-constant-test
            chart_symbol_layer = renderer.symbol
            settings.categoryColors = [
                SymbolConverter.symbol_to_color(c.symbol, context)
                for c in renderer.class_legend.classes
            ]

        if isinstance(chart_symbol_layer, (BarChartSymbol, StackedChartSymbol)):
            if chart_symbol_layer.display_in_3d and context.unsupported_object_callback:
                if context.layer_name:
                    context.unsupported_object_callback(
                        "{}: 3D bar chart was converted to 2d (QGIS does not support 3D bar charts)".format(
                            context.layer_name
                        ),
                        level=Context.WARNING,
                    )
                elif context.symbol_name:
                    context.unsupported_object_callback(
                        "{}: 3D bar chart was converted to 2d (QGIS does not support 3D bar charts)".format(
                            context.symbol_name
                        ),
                        level=Context.WARNING,
                    )
                else:
                    context.unsupported_object_callback(
                        "3D bar chart was converted to 2d (QGIS does not support 3D bar charts)",
                        level=Context.WARNING,
                    )

            if True:  # pylint: disable=using-constant-test
                if renderer.class_legend.classes:
                    first_symbol = renderer.class_legend.classes[0].symbol
                    color = SymbolConverter.symbol_to_line_color(first_symbol, context)
                    if color:
                        settings.penColor = SymbolConverter.symbol_to_line_color(
                            first_symbol, context
                        )
                        settings.penWidth = SymbolConverter.symbol_to_line_width(
                            first_symbol, context
                        )
                    else:
                        settings.penColor = QColor(0, 0, 0, 0)
                    settings.lineSizeUnit = context.units

            if isinstance(chart_symbol_layer, (BarChartSymbol,)):
                try:
                    if chart_symbol_layer.axis_symbol:
                        axis_symbol = SymbolConverter.Symbol_to_QgsSymbol(
                            chart_symbol_layer.axis_symbol, context
                        )
                        settings.setShowAxis(chart_symbol_layer.show_axis)
                        settings.setAxisLineSymbol(axis_symbol)
                except AttributeError:
                    if context.unsupported_object_callback:
                        if context.layer_name:
                            context.unsupported_object_callback(
                                "{}: Bar chart axis symbols require QGIS 3.12 or later".format(
                                    context.layer_name
                                ),
                                level=Context.WARNING,
                            )
                        elif context.symbol_name:
                            context.unsupported_object_callback(
                                "{}: Bar chart axis symbols require QGIS 3.12 or later".format(
                                    context.symbol_name
                                ),
                                level=Context.WARNING,
                            )
                        else:
                            context.unsupported_object_callback(
                                "Bar chart axis symbols require QGIS 3.12 or later",
                                level=Context.WARNING,
                            )

            settings.barWidth = chart_symbol_layer.bar_width * 0.352778

            if isinstance(chart_symbol_layer, (BarChartSymbol,)):
                if chart_symbol_layer.spacing:
                    try:
                        settings.setSpacing(
                            context.convert_size(chart_symbol_layer.spacing)
                        )
                        settings.setSpacingUnit(context.units)
                    except AttributeError:
                        if context.unsupported_object_callback:
                            if context.layer_name:
                                context.unsupported_object_callback(
                                    "{}: Bar chart spacing requires QGIS 3.12 or later".format(
                                        context.layer_name
                                    ),
                                    level=Context.WARNING,
                                )
                        elif context.symbol_name:
                            context.unsupported_object_callback(
                                "{}: Bar chart spacing requires QGIS 3.12 or later".format(
                                    context.symbol_name
                                ),
                                level=Context.WARNING,
                            )
                        else:
                            context.unsupported_object_callback(
                                "Bar chart spacing requires QGIS 3.12 or later",
                                level=Context.WARNING,
                            )

            if not chart_symbol_layer.orientation_vertical:
                settings.diagramOrientation = QgsDiagramSettings.Right

            diagram_renderer = QgsLinearlyInterpolatedDiagramRenderer()
            diagram_renderer.setLowerValue(0)

            if isinstance(chart_symbol_layer, (StackedChartSymbol,)):
                if Qgis.QGIS_VERSION_INT >= 31200:
                    from qgis.core import QgsStackedBarDiagram  # pylint: disable=import-outside-toplevel

                    if chart_symbol_layer.fixed_length:
                        diagram_renderer = QgsSingleCategoryDiagramRenderer()
                        if isinstance(
                            chart_symbol_layer,
                        ):
                            settings.size = QSizeF(
                                context.convert_size(chart_symbol_layer.size),
                                context.convert_size(chart_symbol_layer.size),
                            )
                        else:
                            settings.size = QSizeF(
                                context.convert_size(chart_symbol_layer.max_length),
                                context.convert_size(chart_symbol_layer.max_length),
                            )
                        settings.sizeType = context.units
                    else:
                        expression = "+".join(
                            [
                                QgsExpression.quotedColumnRef(c)
                                for c in renderer.attributes
                            ]
                        )
                        diagram_renderer.setClassificationAttributeIsExpression(True)
                        diagram_renderer.setClassificationAttributeExpression(
                            expression
                        )
                        if isinstance(renderer, ChartRenderer):
                            diagram_renderer.setLowerValue(renderer.min_value or 0)

                        if isinstance(
                            chart_symbol_layer,
                        ):
                            diagram_renderer.setUpperValue(renderer.max_value or 0)
                            diagram_renderer.setUpperSize(
                                QSizeF(
                                    context.convert_size(chart_symbol_layer.size or 0),
                                    context.convert_size(chart_symbol_layer.size or 0),
                                )
                            )
                        else:
                            diagram_renderer.setUpperValue(renderer.symbol.max_value)
                            diagram_renderer.setUpperSize(
                                QSizeF(
                                    context.convert_size(renderer.symbol.max_length),
                                    context.convert_size(renderer.symbol.max_length),
                                )
                            )
                        settings.sizeType = context.units

                    if not chart_symbol_layer.orientation_vertical:
                        settings.diagramOrientation = QgsDiagramSettings.Left
                    else:
                        settings.diagramOrientation = QgsDiagramSettings.Down

                    settings.barWidth = chart_symbol_layer.bar_width
                    diagram_renderer.setDiagram(QgsStackedBarDiagram())

                else:
                    if context.unsupported_object_callback:
                        if context.layer_name:
                            context.unsupported_object_callback(
                                "{}: Stacked charts require QGIS 3.12 or later".format(
                                    context.layer_name
                                ),
                                level=Context.WARNING,
                            )
                    elif context.symbol_name:
                        context.unsupported_object_callback(
                            "{}: Stacked charts require QGIS 3.12 or later".format(
                                context.symbol_name
                            ),
                            level=Context.WARNING,
                        )
                    else:
                        context.unsupported_object_callback(
                            "Stacked charts require QGIS 3.12 or later",
                            level=Context.WARNING,
                        )
                    diagram_renderer.setDiagram(QgsHistogramDiagram())

            else:
                diagram_renderer.setDiagram(QgsHistogramDiagram())

                if True:  # pylint: disable=using-constant-test
                    diagram_renderer.setUpperValue(renderer.symbol.max_value)

                    diagram_renderer.setUpperSize(
                        QSizeF(
                            renderer.symbol.max_length * 0.352778,
                            renderer.symbol.max_length * 0.352778,
                        )
                    )

            diagram_renderer.setDiagramSettings(settings)

            dest_layer.setDiagramRenderer(diagram_renderer)
            dest_layer.setDiagramLayerSettings(layer_settings)
        elif isinstance(chart_symbol_layer, (PieChartSymbol,)):
            if chart_symbol_layer.display_in_3d and context.unsupported_object_callback:
                if context.layer_name:
                    context.unsupported_object_callback(
                        "{}: 3D pie chart was converted to 2d (QGIS does not support 3D pie charts)".format(
                            context.layer_name
                        ),
                        level=Context.WARNING,
                    )
                elif context.symbol_name:
                    context.unsupported_object_callback(
                        "{}: 3D pie chart was converted to 2d (QGIS does not support 3D pie charts)".format(
                            context.symbol_name
                        ),
                        level=Context.WARNING,
                    )
                else:
                    context.unsupported_object_callback(
                        "3D pie chart was converted to 2d (QGIS does not support 3D pie charts)",
                        level=Context.WARNING,
                    )

            if chart_symbol_layer.outline:
                outline = SymbolConverter.Symbol_to_QgsSymbol(
                    chart_symbol_layer.outline, context
                )
                settings.penWidth = outline.width() * 0.352778
                settings.penColor = outline.color()
            else:
                settings.penWidth = 0
                settings.penColor = QColor(0, 0, 0, 0)

            # ArcMap only shows pie charts for features with some non-zero attributes
            exp = " or ".join(settings.categoryAttributes)
            layer_settings.dataDefinedProperties().setProperty(
                QgsDiagramLayerSettings.Show, QgsProperty.fromExpression(exp)
            )

            if True:  # pylint: disable=using-constant-test
                if not renderer.vary_size_by_attribute:
                    diagram_renderer = QgsSingleCategoryDiagramRenderer()
                else:
                    diagram_renderer = QgsLinearlyInterpolatedDiagramRenderer()
                    diagram_renderer.setClassificationField(
                        renderer.vary_size_by_attribute
                    )
                    diagram_renderer.setLowerValue(renderer.min_value)
                    diagram_renderer.setLowerSize(
                        QSizeF(
                            renderer.min_size * 0.352778 * 0.5,
                            renderer.min_size * 0.352778 * 0.5,
                        )
                    )
                    diagram_renderer.setUpperValue(renderer.min_value * 2)
                    diagram_renderer.setUpperSize(
                        QSizeF(
                            renderer.min_size * 0.352778 * 2 * 0.5,
                            renderer.min_size * 0.352778 * 2 * 0.5,
                        )
                    )
                    settings.scaleByArea = False
            diagram_renderer.setDiagram(QgsPieDiagram())
            settings.size = QSizeF(
                context.convert_size(chart_symbol_layer.size),
                context.convert_size(chart_symbol_layer.size),
            )
            settings.sizeType = context.units

            if chart_symbol_layer.clockwise:
                try:
                    settings.setDirection(QgsDiagramSettings.Clockwise)
                except AttributeError:
                    if context.unsupported_object_callback:
                        if context.layer_name:
                            context.unsupported_object_callback(
                                "{}: Clockwise pie charts require QGIS 3.12 or later".format(
                                    context.layer_name
                                ),
                                level=Context.WARNING,
                            )
                    elif context.symbol_name:
                        context.unsupported_object_callback(
                            "{}: Clockwise pie charts require QGIS 3.12 or later".format(
                                context.symbol_name
                            ),
                            level=Context.WARNING,
                        )
                    else:
                        context.unsupported_object_callback(
                            "Clockwise pie charts require QGIS 3.12 or later",
                            level=Context.WARNING,
                        )

            # looks redundant, but actually used by ArcGIS when a diagram has no "global" outline set
            try:
                if True:  # pylint: disable=using-constant-test
                    outline_symbol = SymbolConverter.Symbol_to_QgsSymbol(
                        renderer.class_legend.classes[0].symbol.outline, context
                    ).color()
                    if outline_symbol:
                        settings.penColor = outline_symbol.color()
                        settings.penWidth = outline_symbol.width() * 0.352778

            except AttributeError:
                pass

            if True:  # pylint: disable=using-constant-test
                if not chart_symbol_layer.clockwise:
                    settings.rotationOffset = chart_symbol_layer.starting_angle
                else:
                    settings.rotationOffset = 360.0 - chart_symbol_layer.starting_angle

            diagram_renderer.setDiagramSettings(settings)

            dest_layer.setDiagramRenderer(diagram_renderer)
            dest_layer.setDiagramLayerSettings(layer_settings)

        else:
            raise NotImplementedException(
                "Converting {} diagrams is not yet supported".format(
                    chart_symbol_layer.__class__.__name__
                )
            )

    # pylint: enable=too-many-branches,too-many-statements
