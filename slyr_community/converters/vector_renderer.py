#!/usr/bin/env python

# /***************************************************************************
# vector_renderer.py
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
Vector renderer conversion
"""

from qgis.PyQt.QtCore import Qt
from qgis.core import (
    Qgis,
    QgsWkbTypes,
    QgsExpression,
    QgsLineSymbol,
    QgsMarkerSymbol,
    QgsSingleSymbolRenderer,
    QgsCategorizedSymbolRenderer,
    QgsRendererCategory,
    QgsGraduatedSymbolRenderer,
    QgsRendererRange,
    QgsProperty,
    QgsFillSymbol,
    QgsGeometryGeneratorSymbolLayer,
    QgsRuleBasedRenderer,
    QgsUnitTypes,
    QgsSizeScaleTransformer,
    QgsSymbol,
    QgsNullSymbolRenderer,
    QgsFeatureRenderer,
    QgsSymbolLayer,
    QgsSimpleFillSymbolLayer,
    QgsCentroidFillSymbolLayer
)

from .context import Context
from .expressions import ExpressionConverter
from ..converters.color import ColorConverter
from ..converters.symbols import SymbolConverter
from ..parser.exceptions import NotImplementedException
from ..parser.objects.bi_unique_value_renderer import BiUniqueValueRenderer
from ..parser.objects.chart_renderer import ChartRenderer
from ..parser.objects.class_breaks_renderer import ClassBreaksRenderer
from ..parser.objects.dot_density_renderer import DotDensityRenderer
from ..parser.objects.feature_layer import CustomRenderer
from ..parser.objects.feature_layer import FeatureLayer
from ..parser.objects.fill_symbol_layer import FillSymbolLayer
from ..parser.objects.line_symbol_layer import LineSymbolLayer
from ..parser.objects.marker_symbol_layer import MarkerSymbolLayer
from ..parser.objects.multi_layer_symbols import (
    MultiLayerFillSymbol,
    MultiLayerLineSymbol,
    MultiLayerMarkerSymbol
)
from ..parser.objects.proportional_symbol_renderer import ProportionalSymbolRenderer
from ..parser.objects.representation_renderer import RepresentationRenderer
from ..parser.objects.s52_renderer import S52Renderer
from ..parser.objects.scale_dependent_renderer import ScaleDependentRenderer
from ..parser.objects.simple_renderer import SimpleRenderer
from ..parser.objects.unique_value_renderer import UniqueValueRenderer
from ..parser.objects.units import Units
from ..parser.objects.vector_renderer import VectorRendererBase


class VectorRendererConverter:
    """
    Converts vector renderers
    """

    @staticmethod
    def convert_distance_unit(unit):  # pylint: disable=too-many-return-statements,too-many-branches
        """
        Converts distance units
        """
        if unit == Units.DISTANCE_UNKNOWN:
            return QgsUnitTypes.DistanceUnknownUnit, 1
        elif unit == Units.DISTANCE_INCHES:
            return QgsUnitTypes.DistanceMillimeters, 25.4
        elif unit == Units.DISTANCE_POINTS:
            return QgsUnitTypes.DistanceMillimeters, 0.352778
        elif unit == Units.DISTANCE_FEET:
            return QgsUnitTypes.DistanceFeet, 1
        elif unit == Units.DISTANCE_YARDS:
            return QgsUnitTypes.DistanceYards, 1
        elif unit == Units.DISTANCE_MILES:
            return QgsUnitTypes.DistanceMiles, 1
        elif unit == Units.DISTANCE_NAUTICAL_MILES:
            return QgsUnitTypes.DistanceNauticalMiles, 1
        elif unit == Units.DISTANCE_MILLIMETERS:
            return QgsUnitTypes.DistanceMillimeters, 1
        elif unit == Units.DISTANCE_CENTIMETERS:
            return QgsUnitTypes.DistanceCentimeters, 1
        elif unit == Units.DISTANCE_METERS:
            return QgsUnitTypes.DistanceMeters, 1
        elif unit == Units.DISTANCE_KILOMETERS:
            return QgsUnitTypes.DistanceKilometers, 1
        elif unit == Units.DISTANCE_DECIMAL_DEGREES:
            return QgsUnitTypes.DistanceDegrees, 1
        elif unit == Units.DISTANCE_DECIMETERS:
            return QgsUnitTypes.DistanceCentimeters, 10
        elif False:  # pylint: disable=using-constant-test
            pass
        return None

    @staticmethod
    def conversion_factor_to_meters(units):
        """
        Returns a scale factor for converting to meters
        """
        distance_unit, factor = VectorRendererConverter.convert_distance_unit(units)
        factor = factor * QgsUnitTypes.fromUnitToUnitFactor(distance_unit, QgsUnitTypes.DistanceMeters)
        return factor

    @staticmethod
    def convert_renderer(renderer,  # pylint: disable=too-many-locals,too-many-return-statements,too-many-branches,too-many-statements
                         layer,
                         context: Context, ignore_subheadings: bool = False):
        """
        Converts the renderer from a layer to the QGIS equivalent
        """
        context.symbol_layer_drawing = None
        if layer and hasattr(layer, 'symbol_layer_drawing'):
            context.symbol_layer_drawing = layer.symbol_layer_drawing

        if isinstance(renderer, (SimpleRenderer, )):
            if renderer.symbol:
                context.symbol_name = 'default'
                symbol = SymbolConverter.Symbol_to_QgsSymbol(renderer.symbol, context)
                VectorRendererConverter.apply_renderer_settings_to_symbol(symbol, renderer, context)

                res = QgsSingleSymbolRenderer(symbol)
                return res
            else:
                return QgsNullSymbolRenderer()

        elif isinstance(renderer, (ChartRenderer, )):
            if isinstance(renderer, ChartRenderer) and renderer.symbol2 is not None:
                context.symbol_name = 'default'
                symbol = SymbolConverter.Symbol_to_QgsSymbol(renderer.symbol2, context)
                VectorRendererConverter.apply_renderer_settings_to_symbol(symbol, renderer, context)
                return QgsSingleSymbolRenderer(symbol)
            elif False:  # pylint: disable=using-constant-test
                pass
            else:
                return QgsNullSymbolRenderer()
        elif isinstance(renderer, (ProportionalSymbolRenderer, )):
            context.symbol_name = 'default'
            if isinstance(renderer, ProportionalSymbolRenderer):
                symbol = SymbolConverter.Symbol_to_QgsSymbol(renderer.symbol, context)
            else:
                symbol = None

            # pylint: disable=simplifiable-condition
            if (isinstance(renderer, ProportionalSymbolRenderer) and renderer.proportional_symbol_units != Units.DISTANCE_UNKNOWN) \
                    or (False and renderer.unit_symbolization and renderer.unit_symbolization.value_unit):
                # pylint: enable=simplifiable-condition
                for i in range(symbol.symbolLayerCount()):
                    layer = symbol.symbolLayer(i)
                    if symbol.type() == QgsSymbol.Marker:
                        layer.setSizeUnit(QgsUnitTypes.RenderMetersInMapUnits)
                    else:
                        layer.setWidthUnit(QgsUnitTypes.RenderMetersInMapUnits)

                if isinstance(renderer, ProportionalSymbolRenderer):
                    scale_factor = VectorRendererConverter.conversion_factor_to_meters(renderer.proportional_symbol_units)
                else:
                    scale_factor = 1
                if scale_factor != 1:
                    size_property = QgsProperty.fromExpression('{}*"{}"'.format(scale_factor, renderer.attribute))
                else:
                    size_property = QgsProperty.fromField(renderer.attribute)
            else:
                # need to calculate max size from min size, since ArcMap does this for users without exposing this choice
                if symbol.type() == QgsSymbol.Marker:
                    if renderer.compensate_using_flannery:
                        max_size = symbol.size() * 5.5 + 1.34
                    else:
                        max_size = symbol.size() * 5
                    min_size = symbol.size()
                else:
                    max_size = symbol.width() * 2
                    min_size = symbol.width()
                size_property = QgsProperty.fromField(renderer.attribute)

                if isinstance(renderer, ProportionalSymbolRenderer):
                    scale_type = QgsSizeScaleTransformer.Flannery if renderer.compensate_using_flannery else QgsSizeScaleTransformer.Linear
                else:
                    scale_type = QgsSizeScaleTransformer.Flannery

                transformer = QgsSizeScaleTransformer(
                    type=scale_type,
                    minValue=renderer.value_min,
                    maxValue=renderer.value_max,
                    minSize=min_size,
                    maxSize=max_size)

                size_property.setTransformer(transformer)

            if symbol.type() == QgsSymbol.Marker:
                symbol.setDataDefinedSize(size_property)
            else:
                symbol.setDataDefinedWidth(size_property)

            VectorRendererConverter.apply_renderer_settings_to_symbol(symbol, renderer, context)

            background_symbol = SymbolConverter.Symbol_to_QgsSymbol(renderer.background_symbol,
                                                                    context) if renderer.background_symbol else None

            uses_symbol_levels = False
            if QgsWkbTypes.geometryType(
                    context.layer_type_hint) == QgsWkbTypes.PolygonGeometry and symbol.type() == QgsSymbol.Marker:
                polygon_symbol = background_symbol.clone()
                for i in range(polygon_symbol.symbolLayerCount()):
                    polygon_symbol.symbolLayer(i).setRenderingPass(i)

                centroid_fill = QgsCentroidFillSymbolLayer()
                centroid_fill.setSubSymbol(symbol)
                i = polygon_symbol.symbolLayerCount()
                centroid_fill.setRenderingPass(i)
                polygon_symbol.appendSymbolLayer(centroid_fill)
                symbol = polygon_symbol
                uses_symbol_levels = True

            if not renderer.exclusion_filter:
                res = QgsSingleSymbolRenderer(symbol)
            else:
                rootrule = QgsRuleBasedRenderer.Rule(None)
                rule = QgsRuleBasedRenderer.Rule(symbol, 0, 0, 'NOT ({})'.format(renderer.exclusion_filter))
                rootrule.appendChild(rule)
                res = QgsRuleBasedRenderer(rootrule)

            res.setUsingSymbolLevels(uses_symbol_levels)

            return res

        # pylint: disable=too-many-nested-blocks
        elif isinstance(renderer, (UniqueValueRenderer, )):
            requires_rule_based = False
            class_count = 0
            for g in renderer.groups:
                class_count += len(g.classes)
                if g.heading and (', '.join(renderer.fields)).upper() != g.heading.upper():
                    requires_rule_based = True

            use_rule_based = requires_rule_based and not ignore_subheadings
            if requires_rule_based and Qgis.QGIS_VERSION_INT < 31700:
                # QGIS < 3.18 has issues with large number of rule based rules and gdb files
                use_rule_based = False

            if requires_rule_based and not use_rule_based:
                for g in renderer.groups:
                    if context.unsupported_object_callback:
                        context.unsupported_object_callback(
                            'Unique Value legend group title “{}” is not supported by QGIS'.format(
                                g.heading),
                            level=Context.WARNING)

            fields = renderer.fields[:]
            if context.main_layer_name:
                fields = [f.replace(context.main_layer_name + '.', '') for f in fields]

            if len(fields) == 1:
                cat_exp = QgsExpression.quotedColumnRef(fields[0])
            elif isinstance(renderer, UniqueValueRenderer):
                cat_exp = 'concat({})'.format(
                    ",'{}',".format(renderer.concatenator).join(['"{}"'.format(f) for f in fields]))
            elif False:  # pylint: disable=using-constant-test
                pass

            if False:  # pylint: disable=using-constant-test
                pass
            else:
                renderer_default_symbol = renderer.symbol
                all_other_label = renderer.all_other_value
                include_default = renderer.include_all_other

            if use_rule_based:
                rootrule = QgsRuleBasedRenderer.Rule(None)

                i = 0
                found_all_other = False
                for g in renderer.groups:
                    if g.heading:
                        heading_rule = QgsRuleBasedRenderer.Rule(None, 0, 0, '', g.heading, g.heading)
                        rootrule.appendChild(heading_rule)
                    else:
                        heading_rule = None

                    for c in g.classes:
                        context.symbol_name = c.label
                        if renderer_default_symbol == c.symbol:
                            val = None
                            found_all_other = True
                        else:
                            if False:  # pylint: disable=using-constant-test
                                pass
                            else:
                                val = renderer.values[i]
                                i += 1
                        symbol = SymbolConverter.Symbol_to_QgsSymbol(c.symbol, context)
                        VectorRendererConverter.apply_renderer_settings_to_symbol(symbol, renderer, context)

                        if isinstance(val, list):
                            filter_string = '{} in ({})'.format(cat_exp,
                                                                ', '.join(QgsExpression.quotedValue(v) for v in val))
                        elif val is None:
                            filter_string = '{} IS NULL'.format(cat_exp)
                        else:
                            filter_string = '{} = {}'.format(cat_exp, QgsExpression.quotedValue(val))
                        rule = QgsRuleBasedRenderer.Rule(symbol, 0, 0,
                                                         filter_string,
                                                         c.label, c.label)
                        if heading_rule:
                            heading_rule.appendChild(rule)
                        else:
                            rootrule.appendChild(rule)

                if renderer_default_symbol and not found_all_other:
                    default_symbol = SymbolConverter.Symbol_to_QgsSymbol(renderer_default_symbol, context)

                    all_other_rule = QgsRuleBasedRenderer.Rule(default_symbol, 0, 0, '', all_other_label,
                                                               all_other_label, True)
                    all_other_rule.setActive(include_default)
                    rootrule.appendChild(all_other_rule)

                res = QgsRuleBasedRenderer(rootrule)

                return res

            else:
                i = 0
                cats = []
                found_all_other = False
                for g in renderer.groups:

                    for c in g.classes:
                        context.symbol_name = c.label
                        if renderer_default_symbol == c.symbol:
                            val = None
                            found_all_other = True
                        else:
                            if False:  # pylint: disable=using-constant-test
                                pass
                            else:
                                val = renderer.values[i]

                                i += 1
                        symbol = SymbolConverter.Symbol_to_QgsSymbol(c.symbol, context)
                        VectorRendererConverter.apply_renderer_settings_to_symbol(symbol, renderer, context)

                        cat = QgsRendererCategory(val, symbol, c.label)
                        cats.append(cat)

                if found_all_other:
                    for c in cats:
                        if c.value() == '':
                            # this is a hack! If there's both an "all other categories" class AND
                            # an empty string class, then ArcMap matches only the "all other categories"
                            # class. But QGIS will treat BOTH as "all other values", so we get the wrong
                            # rendered match. Let's hack around this by replacing the value for the
                            # unwanted category with a zero-width space instead
                            c.setValue('\u200c')

                if not cats and not include_default:
                    # this is a workaround I've seen made in LYRs in place of a real "no symbol" renderer.
                    # users will create a unique values renderer with only the "all other values" class, but then
                    # disable that class. The end result is that labels are STILL shown for all features in this layer,
                    # even though the features aren't being rendered. Ie- same as QGIS null symbol renderer
                    return QgsNullSymbolRenderer()

                if renderer_default_symbol and not found_all_other:
                    default_symbol = SymbolConverter.Symbol_to_QgsSymbol(renderer_default_symbol, context)
                    cat = QgsRendererCategory(None, default_symbol, all_other_label,
                                              include_default)
                    cats.append(cat)

                res = QgsCategorizedSymbolRenderer(cat_exp, cats)

                if False:  # pylint: disable=using-constant-test
                    pass

                return res
        # pylint: enable=too-many-nested-blocks
        elif isinstance(renderer, BiUniqueValueRenderer):
            # first convert main renderer to a categorized renderer
            res = VectorRendererConverter.convert_renderer(renderer.main_renderer, layer, context, True)

            # then set data defined sizes/colors on all symbols
            for idx, cat in enumerate(res.categories()):
                sym = cat.symbol().clone()

                exp_parts = []
                for i, r in enumerate(renderer.variation_renderer.ranges):

                    symbol = SymbolConverter.Symbol_to_QgsSymbol(
                        renderer.variation_renderer.legend_group.classes[i].symbol, context)

                    if renderer.variation_renderer.is_graduated_symbol:
                        if symbol.type() == QgsSymbol.Marker:
                            val = symbol.size()
                        elif symbol.type() == QgsSymbol.Line:
                            val = symbol.width()
                        else:
                            assert False
                    else:
                        val = "'{}'".format(symbol.color().name())

                    exp_parts.append(
                        '  when "{0}" >= {1} and "{0}" <= {2} then {3}'.format(renderer.variation_renderer.attribute,
                                                                               r[0], r[1], val))

                prop = QgsProperty.fromExpression('case\n{}\nend'.format('\n'.join(exp_parts)))
                if renderer.variation_renderer.is_graduated_symbol:
                    sym.setDataDefinedSize(prop)
                else:
                    for symbol_layer in range(sym.symbolLayerCount()):
                        if sym.type() == QgsSymbol.Line:
                            sym.symbolLayer(symbol_layer).setDataDefinedProperty(QgsSymbolLayer.PropertyStrokeColor, prop)
                        elif sym.type() == QgsSymbol.Marker:
                            sym.symbolLayer(symbol_layer).setDataDefinedProperty(QgsSymbolLayer.PropertyFillColor, prop)
                        # fill symbols seem to ignore the variation renderer?

                res.updateCategorySymbol(idx, sym)

            return res

        elif isinstance(renderer, DotDensityRenderer):
            if Qgis.QGIS_VERSION_INT < 31100 and context.unsupported_object_callback:
                context.unsupported_object_callback(
                    '{}: Dot density renderers require QGIS 3.12 or later'.format(
                        context.layer_name or context.symbol_name),
                    level=Context.CRITICAL)
                return QgsSingleSymbolRenderer(QgsFillSymbol())

            if len(renderer.fields) > 1:
                context.unsupported_object_callback(
                    '{}: Dot density renderers with multiple attributes must cannot be merged into a single symbol in QGIS'.format(
                        context.layer_name),
                    level=Context.WARNING)
            if renderer.mask_layer:
                context.unsupported_object_callback(
                    '{}: Dot density renderers with mask layers are not supported in QGIS'.format(
                        context.layer_name),
                    level=Context.WARNING)

            from qgis.core import QgsRandomMarkerFillSymbolLayer  # pylint: disable=import-outside-toplevel

            s = QgsFillSymbol()
            if renderer.fill_symbol.background_color:
                background = QgsSimpleFillSymbolLayer(
                    ColorConverter.color_to_qcolor(renderer.fill_symbol.background_color), strokeStyle=Qt.NoPen)
                s.appendSymbolLayer(background)

            for i, f in enumerate(renderer.fields):
                symbol_layer = QgsRandomMarkerFillSymbolLayer(1, method=QgsRandomMarkerFillSymbolLayer.AbsoluteCount)
                if renderer.maintain_density and renderer.maintain_density_by_dot_value:
                    exp = '("{}" * {}) / ({} * @map_scale)'.format(f, renderer.scale, renderer.dot_value)
                else:
                    exp = '"{}" / {}'.format(f, renderer.dot_value)
                symbol_layer.setDataDefinedProperty(QgsSymbolLayer.PropertyPointCount,
                                                    QgsProperty.fromExpression(exp))
                symbol_layer.setSeed(renderer.fill_symbol.seed)
                symbol_layer.setClipPoints(False)

                marker = SymbolConverter.Symbol_to_QgsSymbol(renderer.fill_symbol.markers[len(renderer.fields) - i - 1],
                                                             context)
                if renderer.maintain_density and not renderer.maintain_density_by_dot_value:
                    marker.setDataDefinedSize(
                        QgsProperty.fromExpression('{} * {} / @map_scale'.format(marker.size(), renderer.scale)))

                symbol_layer.setSubSymbol(marker)
                s.appendSymbolLayer(symbol_layer)

            outline = SymbolConverter.Symbol_to_QgsSymbol(renderer.fill_symbol.outline_symbol, context)
            start = s.symbolLayerCount()
            for symbol_layer_index in range(outline.symbolLayerCount()):
                s.insertSymbolLayer(start, outline.symbolLayer(symbol_layer_index).clone())

            s.deleteSymbolLayer(0)
            s.setClipFeaturesToExtent(False)
            return QgsSingleSymbolRenderer(s)

        elif isinstance(renderer, (ClassBreaksRenderer, )):
            i = 0
            cats = []

            if isinstance(renderer, ClassBreaksRenderer) and renderer.legend_group.heading and renderer.legend_group.heading != renderer.attribute and context.unsupported_object_callback:
                context.unsupported_object_callback(
                    'Class Break legend group title “{}” is not supported by QGIS'.format(
                        renderer.legend_group.heading),
                    level=Context.WARNING)

            background_symbol = SymbolConverter.Symbol_to_QgsSymbol(renderer.background_symbol,
                                                                    context) if renderer.background_symbol else None

            if isinstance(renderer, ClassBreaksRenderer):
                classes = renderer.legend_group.classes
            else:
                classes = []
            for c in classes:
                context.symbol_name = c.label

                if isinstance(renderer, ClassBreaksRenderer):
                    range_index = i if renderer.sort_ascending else len(renderer.ranges) - i - 1
                else:
                    range_index = 0

                if isinstance(renderer, ClassBreaksRenderer):
                    lower = renderer.ranges[range_index][0]
                    upper = renderer.ranges[range_index][1]
                else:
                    lower = 0
                    upper = 0
                i += 1
                symbol = SymbolConverter.Symbol_to_QgsSymbol(c.symbol, context)
                VectorRendererConverter.apply_renderer_settings_to_symbol(symbol, renderer, context)

                if QgsWkbTypes.geometryType(
                        context.layer_type_hint) == QgsWkbTypes.PolygonGeometry and symbol.type() == QgsSymbol.Marker:
                    centroid_fill = QgsCentroidFillSymbolLayer()
                    centroid_fill.setSubSymbol(symbol)

                    if background_symbol is not None:
                        polygon_symbol = background_symbol.clone()
                        polygon_symbol.appendSymbolLayer(centroid_fill)
                    else:
                        polygon_symbol = QgsFillSymbol()
                        polygon_symbol.changeSymbolLayer(0, centroid_fill)

                    symbol = polygon_symbol

                cat = QgsRendererRange(lower, upper, symbol, c.label)
                cats.append(cat)

            if isinstance(renderer,ClassBreaksRenderer):
                if renderer.normalization_method == VectorRendererBase.NORMALIZE_BY_PERCENT_OF_TOTAL:
                    attr = '{}/sum({})*100'.format(renderer.attribute, renderer.attribute)
                elif renderer.normalization_method != VectorRendererBase.NORMALIZE_BY_NOTHING and context.unsupported_object_callback:
                    context.unsupported_object_callback(
                        'Class Break normalization method “{}” is not supported by QGIS'.format(
                            VectorRendererBase.normalize_method_to_string(renderer.normalization_method)),
                        level=Context.CRITICAL)
                    attr = renderer.attribute
                else:
                    attr = renderer.attribute
            else:
                pass

            res = QgsGraduatedSymbolRenderer(attr, cats)
            if isinstance(renderer, ClassBreaksRenderer) and renderer.is_graduated_symbol:
                res.setGraduatedMethod(QgsGraduatedSymbolRenderer.GraduatedSize)
            elif False:  # pylint: disable=using-constant-test
                pass

            if False:  # pylint: disable=using-constant-test
                pass

            return res

        elif isinstance(renderer, ScaleDependentRenderer):
            for r in renderer.renderers:
                if not isinstance(r, SimpleRenderer):
                    if context.unsupported_object_callback:
                        context.unsupported_object_callback(
                            'Scale dependant renderer with complex child renderers cannot be converted',
                            level=Context.CRITICAL)
                        return None

                    raise NotImplementedException(
                        '{} renderers cannot be converted yet'.format(renderer.__class__.__name__))

            rootrule = QgsRuleBasedRenderer.Rule(None)
            for i, r in enumerate(renderer.renderers):
                max_scale = renderer.breaks[i - 1] if i > 0 else 0
                if max_scale > 2147483647:
                    # avoid overflows
                    max_scale = 0
                min_scale = renderer.breaks[i]
                if min_scale > 2147483647:
                    min_scale = 0

                symbol = SymbolConverter.Symbol_to_QgsSymbol(r.symbol, context)

                rule = QgsRuleBasedRenderer.Rule(symbol, int(round(max_scale)), int(round(min_scale)), '')
                rootrule.appendChild(rule)

            res = QgsRuleBasedRenderer(rootrule)
            return res

        elif isinstance(renderer, RepresentationRenderer):
            if context.layer_type_hint is not None:
                symbol = None
                if QgsWkbTypes.geometryType(context.layer_type_hint) == QgsWkbTypes.PointGeometry:
                    symbol = QgsMarkerSymbol()

                elif QgsWkbTypes.geometryType(context.layer_type_hint) == QgsWkbTypes.LineGeometry:
                    symbol = QgsLineSymbol()
                elif QgsWkbTypes.geometryType(context.layer_type_hint) == QgsWkbTypes.PolygonGeometry:
                    symbol = QgsFillSymbol()

                if symbol:
                    if context.unsupported_object_callback:
                        context.unsupported_object_callback(
                            'Representation renderers are not well supported in QGIS, feature styling has been dropped',
                            level=Context.CRITICAL)
                    symbol_layer = QgsGeometryGeneratorSymbolLayer.create({})
                    symbol_layer.setSymbolType(symbol.type())
                    symbol_layer.setGeometryExpression('get_representation_geometry()')
                    symbol.changeSymbolLayer(0, symbol_layer)
                    return QgsSingleSymbolRenderer(symbol)

            if context.unsupported_object_callback:
                context.unsupported_object_callback(
                    'Representation renderers could not be converted',
                    level=Context.CRITICAL)
            return None
        elif isinstance(renderer, S52Renderer):
            if context.unsupported_object_callback:
                context.unsupported_object_callback(
                    '{}: S52 Renderers are not supported by QGIS'.format(
                        context.layer_name or context.symbol_name),
                    level=Context.CRITICAL)
            return QgsFeatureRenderer.defaultRenderer(QgsWkbTypes.geometryType(context.layer_type_hint))
        elif isinstance(renderer, CustomRenderer):
            if context.unsupported_object_callback:
                context.unsupported_object_callback(
                    '{}: Layer had a renderer provided by a custom extension, this could not be converted'.format(
                        context.layer_name or context.symbol_name),
                    level=Context.CRITICAL)
            return QgsFeatureRenderer.defaultRenderer(QgsWkbTypes.geometryType(context.layer_type_hint))

        raise NotImplementedException('{} renderers cannot be converted yet'.format(renderer.__class__.__name__))

    @staticmethod
    def apply_data_defined_color_to_symbol(symbol: QgsSymbol, expression):
        """
        Applies data defined color to a symbol
        """
        prop = QgsProperty.fromExpression(expression)
        for symbol_layer_index in range(symbol.symbolLayerCount()):
            layer = symbol.symbolLayer(symbol_layer_index)
            layer.setDataDefinedProperty(QgsSymbolLayer.PropertyFillColor, prop)
            layer.setDataDefinedProperty(QgsSymbolLayer.PropertyStrokeColor, prop)
            layer.setDataDefinedProperty(QgsSymbolLayer.PropertySecondaryColor, prop)
            if layer.subSymbol() is not None:
                VectorRendererConverter.apply_data_defined_color_to_symbol(layer.subSymbol(), expression)

    # pylint: disable=too-many-branches
    @staticmethod
    def apply_renderer_settings_to_symbol(symbol: QgsSymbol, renderer, context: Context):
        """
        Applies renderer level settings to a symbol, i.e. data defined overrides
        """
        if False:  # pylint: disable=using-constant-test
            return

        if False:  # pylint: disable=using-constant-test
            return

        if renderer.transparency_attribute:
            if Qgis.QGIS_VERSION_INT >= 31800:
                symbol.setDataDefinedProperty(QgsSymbol.PropertyOpacity,
                                              QgsProperty.fromExpression('100-"{}"'.format(renderer.transparency_attribute)))
            else:
                opacity_expression = 'set_color_part(@value, \'alpha\',  (100-"{}")*255/100 )'.format(
                    renderer.transparency_attribute)
                VectorRendererConverter.apply_data_defined_color_to_symbol(symbol, opacity_expression)
        if renderer.graduated_size_type == VectorRendererBase.SIZE_EXPRESSION:
            size_expression = ExpressionConverter.convert_vbscript_expression(renderer.graduated_expression, context)
            if isinstance(symbol, QgsMarkerSymbol):
                symbol.setDataDefinedSize(QgsProperty.fromExpression(size_expression))
            elif isinstance(symbol, QgsLineSymbol):
                symbol.setDataDefinedWidth(QgsProperty.fromExpression(size_expression))
        elif renderer.graduated_size_type == VectorRendererBase.SIZE_RANDOM:
            size_expression = 'randf({}, {}, seed:=coalesce($id, 0))'.format(renderer.random_size_min,
                                                                             renderer.random_size_max)
            if isinstance(symbol, QgsMarkerSymbol):
                symbol.setDataDefinedSize(QgsProperty.fromExpression(size_expression))
            elif isinstance(symbol, QgsLineSymbol):
                symbol.setDataDefinedWidth(QgsProperty.fromExpression(size_expression))

        if renderer.rotate_flag_3d == VectorRendererBase.ROTATE_FLAG_3D_EXPRESSION_Z:
            if renderer.rotation_attribute and isinstance(symbol, QgsMarkerSymbol):
                if renderer.rotation_type == VectorRendererBase.ROTATE_SYMBOL_ARITHMETIC:
                    rotation_expression = '90 - "{}"'.format(renderer.rotation_attribute)
                    symbol.setDataDefinedAngle(QgsProperty.fromExpression(rotation_expression))
                elif renderer.rotation_type == VectorRendererBase.ROTATE_SYMBOL_GEOGRAPHIC:
                    symbol.setDataDefinedAngle(QgsProperty.fromField(renderer.rotation_attribute))
                else:
                    assert False, 'Unknown rotation type'
            elif renderer.rotation_expression_z and isinstance(symbol, QgsMarkerSymbol):
                if renderer.rotation_type == VectorRendererBase.ROTATE_SYMBOL_ARITHMETIC:
                    rotation_expression = '90 - {}'.format(
                        ExpressionConverter.convert(renderer.rotation_expression_z, None, False, context))
                    symbol.setDataDefinedAngle(QgsProperty.fromExpression(rotation_expression))
                elif renderer.rotation_type == VectorRendererBase.ROTATE_SYMBOL_GEOGRAPHIC:
                    rotation_expression = ExpressionConverter.convert(renderer.rotation_expression_z, None, False,
                                                                      context)
                    symbol.setDataDefinedAngle(QgsProperty.fromExpression(rotation_expression))
                else:
                    assert False, 'Unknown rotation type'
        elif renderer.rotate_flag_3d == VectorRendererBase.ROTATE_FLAG_3D_RANDOM_Z:
            rotate_expression = 'randf({}, {}, seed:=coalesce($id, 0))'.format(renderer.random_rotation_min_z,
                                                                               renderer.random_rotation_max_z)
            if renderer.rotation_type == VectorRendererBase.ROTATE_SYMBOL_ARITHMETIC:
                rotate_expression = '90 - ({})'.format(rotate_expression)
            elif renderer.rotation_type == VectorRendererBase.ROTATE_SYMBOL_GEOGRAPHIC:
                pass
            else:
                assert False, 'Unknown rotation type'
            symbol.setDataDefinedAngle(QgsProperty.fromExpression(rotate_expression))

    # pylint: enable=too-many-branches

    @staticmethod
    def guess_geometry_type_from_renderer(layer: FeatureLayer):
        """
        Infers a layer's geometry type from the renderer's symbols
        """
        renderer = layer.renderer

        if isinstance(renderer, (SimpleRenderer, )):
            return VectorRendererConverter.wkb_type_from_symbol(renderer.symbol)
        elif isinstance(renderer, UniqueValueRenderer):
            return VectorRendererConverter.wkb_type_from_symbol(renderer.symbol)
        elif False:  # pylint: disable=using-constant-test
            pass
        elif isinstance(renderer, ClassBreaksRenderer):
            if renderer.legend_group and renderer.legend_group.classes:
                return VectorRendererConverter.wkb_type_from_symbol(renderer.legend_group.classes[0].symbol)
        elif False:  # pylint: disable=using-constant-test
            pass
        elif False:  # pylint: disable=using-constant-test
            pass
        elif False:  # pylint: disable=using-constant-test
            pass
        return None

    @staticmethod
    def wkb_type_from_symbol(symbol):
        """
        Guess a layer's WKB type using a symbol
        """
        if False:  # pylint: disable=using-constant-test
            pass

        if isinstance(symbol, (MultiLayerFillSymbol, FillSymbolLayer, )):
            return QgsWkbTypes.MultiPolygon
        elif isinstance(symbol, (MultiLayerLineSymbol, LineSymbolLayer, )):
            return QgsWkbTypes.MultiLineString
        elif isinstance(symbol, (MultiLayerMarkerSymbol, MarkerSymbolLayer, )):
            return QgsWkbTypes.Point

        return QgsWkbTypes.Unknown

    @staticmethod
    def extract_symbols_from_renderer(layer: FeatureLayer, context: Context, default_name='default', base_name=''):
        """
        Returns a dictionary containing all symbols ripped from a feature layer
        """
        renderer = layer.renderer

        symbols = {}
        if isinstance(renderer, (SimpleRenderer, )):
            name = base_name if base_name else default_name
            context.symbol_name = name
            symbols[name] = SymbolConverter.Symbol_to_QgsSymbol(renderer.symbol, context)
        elif isinstance(renderer, UniqueValueRenderer):
            for g in renderer.groups:
                for c in g.classes:
                    name = '{} {}'.format(base_name, c.label) if base_name else c.label
                    context.symbol_name = name
                    symbols[name] = SymbolConverter.Symbol_to_QgsSymbol(c.symbol, context)
        elif False:  # pylint: disable=using-constant-test
            pass
        elif isinstance(renderer, ClassBreaksRenderer):
            for c in renderer.legend_group.classes:
                name = '{} {}'.format(base_name, c.label) if base_name else c.label
                context.symbol_name = name
                symbols[name] = SymbolConverter.Symbol_to_QgsSymbol(c.symbol, context)
        elif False:  # pylint: disable=using-constant-test
            pass

        if isinstance(layer, FeatureLayer):
            if layer.annotation_collection and layer.annotation_collection.properties:
                for p in layer.annotation_collection.properties:
                    name = base_name if base_name else default_name
                    context.symbol_name = name + ' labels'
                    symbols[context.symbol_name] = SymbolConverter.Symbol_to_QgsSymbol(p.text_symbol, context)

        return symbols
