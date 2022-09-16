#!/usr/bin/env python

# /***************************************************************************
# labels.py
# ----------
# Date                 : September 2019
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
Label conversion
"""
from qgis.core import (
    Qgis,
    QgsPalLayerSettings,
    QgsWkbTypes,
    QgsVectorLayer,
    QgsVectorLayerSimpleLabeling,
    QgsRuleBasedLabeling,
    QgsProperty,
    QgsUnitTypes,
    QgsMargins
)

from .expressions import ExpressionConverter
from .text_format import TextSymbolConverter
from ..parser.exceptions import NotImplementedException
from ..parser.objects.annotate_layer_properties_collection import AnnotateLayerPropertiesCollection
from ..parser.objects.balloon_callout import BalloonCallout
from ..parser.objects.basic_overposter_layer_properties import BasicOverposterLayerProperties
from ..parser.objects.label_engine_layer_properties import LabelEngineLayerProperties
from ..parser.objects.label_style import LabelStyle
from ..parser.objects.line_callout import LineCallout
from ..parser.objects.maplex_overposter_layer_properties import MaplexOverposterLayerProperties
from ..parser.objects.maplex_label_engine_layer_properties import MaplexLabelEngineLayerProperties
from ..parser.objects.maplex_rotation_properties import MaplexRotationProperties
from ..parser.objects.marker_text_background import MarkerTextBackground
from ..parser.objects.simple_line_callout import SimpleLineCallout
from ..parser.objects.text_symbol import TextSymbol


class LabelConverter:
    """
    Label converter
    """

    TEXT_ALIGN_MAP = {
        TextSymbol.HALIGN_LEFT: QgsPalLayerSettings.MultiLeft,
        TextSymbol.HALIGN_CENTER: QgsPalLayerSettings.MultiCenter,
        TextSymbol.HALIGN_RIGHT: QgsPalLayerSettings.MultiRight,
        TextSymbol.HALIGN_FULL: QgsPalLayerSettings.MultiLeft,  # doesn't directly map
    }

    OBSTACLE_WEIGHT_MAP = {
        BasicOverposterLayerProperties.WEIGHT_NONE: 0,
        BasicOverposterLayerProperties.WEIGHT_LOW: 0.5,
        BasicOverposterLayerProperties.WEIGHT_MED: 1.0,
        BasicOverposterLayerProperties.WEIGHT_HIGH: 2.0,
    }

    LABEL_WEIGHT_MAP = {
        BasicOverposterLayerProperties.WEIGHT_NONE: 0,
        BasicOverposterLayerProperties.WEIGHT_LOW: 2,
        BasicOverposterLayerProperties.WEIGHT_MED: 5,
        BasicOverposterLayerProperties.WEIGHT_HIGH: 10,
    }

    @staticmethod
    def convert_annotation_collection(collection: AnnotateLayerPropertiesCollection, dest_layer: QgsVectorLayer,
                                      context):
        """
        Converts an annotation collection to QGIS labeling
        """
        if not collection:
            return

        if isinstance(collection, AnnotateLayerPropertiesCollection):
            properties = collection.properties
        else:
            properties = collection

        if len(properties) == 1 and not properties[0].class_filter:
            # one label class, use simple labeling
            properties = properties[0]
            label_settings = LabelConverter.convert_label_engine_layer_properties(properties,
                                                                                  layer_geometry_type=dest_layer.geometryType(),
                                                                                  context=context)
            label_settings.drawLabels = properties.label_features

            labeling = QgsVectorLayerSimpleLabeling(label_settings)
            dest_layer.setLabeling(labeling)
        else:
            # multiple classes, use rule-based labeling
            root_rule = QgsRuleBasedLabeling.Rule(None)
            for p in properties:
                label_settings = LabelConverter.convert_label_engine_layer_properties(p,
                                                                                      layer_geometry_type=dest_layer.geometryType(),
                                                                                      context=context)

                zoom_max = p.scale_range_min or 0
                zoom_min = p.scale_range_max or 0
                if zoom_max and zoom_min and zoom_max > zoom_min:
                    zoom_min, zoom_max = zoom_max, zoom_min

                rule = QgsRuleBasedLabeling.Rule(label_settings, zoom_max, zoom_min,
                                                 ExpressionConverter.convert_esri_sql(p.class_filter) if p.class_filter else '',
                                                 p.class_name)
                rule.setActive(p.label_features)
                root_rule.appendChild(rule)
            labeling = QgsRuleBasedLabeling(root_rule)
            dest_layer.setLabeling(labeling)

    @staticmethod
    def convert_label_text_symbol(text_symbol, dest_label_settings, context, reference_scale=None):
        """
        Converts the label text symbol
        """
        text_format = TextSymbolConverter.text_symbol_to_qgstextformat(text_symbol, context, reference_scale)

        if text_symbol.background_symbol:
            callout = LabelConverter.convert_callout(text_symbol.background_symbol, context, reference_scale)
            if callout:
                dest_label_settings.setCallout(callout)
                if isinstance(text_symbol.background_symbol, BalloonCallout):
                    # we don't want double up of background vs callout for symbol, so remove background symbol
                    # from text format
                    background = text_format.background()
                    background.setEnabled(False)
                    text_format.setBackground(background)

        dest_label_settings.setFormat(text_format)
        dest_label_settings.multilineAlign = LabelConverter.TEXT_ALIGN_MAP[text_symbol.horizontal_alignment]

    @staticmethod
    def convert_overposter(overposter,  # pylint: disable=too-many-branches,too-many-statements
                           maplex_overposter,
                           layer_geometry_type,
                           dest_label_settings,
                           context):
        """
        Converts overposter settings
        """

        if layer_geometry_type in (QgsWkbTypes.PointGeometry, QgsWkbTypes.UnknownGeometry):
            if overposter.point_placement_method == BasicOverposterLayerProperties.POINT_PLACEMENT_ON_TOP:
                dest_label_settings.placement = QgsPalLayerSettings.OverPoint
            elif overposter.point_placement_method == BasicOverposterLayerProperties.POINT_PLACEMENT_AROUND:
                dest_label_settings.placement = QgsPalLayerSettings.OrderedPositionsAroundPoint
                if overposter.point_placement_priorities:
                    priorities = []
                    for i in range(1, 4):
                        if 'TR' not in priorities and overposter.point_placement_priorities.top_right == i:
                            priorities.append('TR')
                        if 'TL' not in priorities and overposter.point_placement_priorities.top_left == i:
                            priorities.append('TL')
                        if 'BR' not in priorities and overposter.point_placement_priorities.bottom_right == i:
                            priorities.append('BR')
                        if 'BL' not in priorities and overposter.point_placement_priorities.bottom_left == i:
                            priorities.append('BL')
                        if 'R' not in priorities and overposter.point_placement_priorities.center_right == i:
                            priorities.append('R')
                        if 'L' not in priorities and overposter.point_placement_priorities.center_left == i:
                            priorities.append('L')
                        if 'T' not in priorities and overposter.point_placement_priorities.top_center == i:
                            priorities.append('T')
                        if 'B' not in priorities and overposter.point_placement_priorities.bottom_center == i:
                            priorities.append('B')
                    dd = dest_label_settings.dataDefinedProperties()
                    dd.setProperty(QgsPalLayerSettings.PredefinedPositionOrder,
                                   QgsProperty.fromExpression("'{}'".format(','.join(priorities))))
                    dest_label_settings.setDataDefinedProperties(dd)
            else:
                # for now - TODO  POINT_PLACEMENT_ROTATION_FIELD , POINT_PLACEMENT_SPECIFIED_ANGLES
                dest_label_settings.placement = QgsPalLayerSettings.AroundPoint
        elif layer_geometry_type == QgsWkbTypes.LineGeometry:
            placement_flags = 0
            try:
                # TODO - horizontal
                dest_label_settings.placement = QgsPalLayerSettings.Horizontal if overposter.line_label_position.horizontal else QgsPalLayerSettings.Curved if overposter.line_label_position.curved else QgsPalLayerSettings.Line

                if overposter.line_label_position.below:
                    placement_flags |= QgsPalLayerSettings.BelowLine
                if overposter.line_label_position.above:
                    placement_flags |= QgsPalLayerSettings.AboveLine
                if overposter.line_label_position.online:
                    placement_flags |= QgsPalLayerSettings.OnLine
                if False:  # pylint: disable=using-constant-test
                    pass
                else:
                    if not overposter.line_label_position.follow_line_orientation:
                        placement_flags |= QgsPalLayerSettings.MapOrientation
            except AttributeError:
                if maplex_overposter:
                    if maplex_overposter.line_placement_method in (MaplexOverposterLayerProperties.LINE_PLACEMENT_CENTERED_HORIZONTAL_ON_LINE, ):
                        dest_label_settings.placement = QgsPalLayerSettings.Horizontal
                        placement_flags = QgsPalLayerSettings.OnLine | QgsPalLayerSettings.MapOrientation
                    elif maplex_overposter.line_placement_method in (MaplexOverposterLayerProperties.LINE_PLACEMENT_CENTERED_STRAIGHT_ON_LINE,):
                        dest_label_settings.placement = QgsPalLayerSettings.Line
                        placement_flags = QgsPalLayerSettings.OnLine | QgsPalLayerSettings.MapOrientation
                    elif maplex_overposter.line_placement_method in (MaplexOverposterLayerProperties.LINE_PLACEMENT_CENTERED_CURVED_ON_LINE, ):
                        dest_label_settings.placement = QgsPalLayerSettings.Curved
                        placement_flags = QgsPalLayerSettings.OnLine | QgsPalLayerSettings.MapOrientation
                    elif maplex_overposter.line_placement_method in (MaplexOverposterLayerProperties.LINE_PLACEMENT_CENTERED_PERPENDICULAR_ON_LINE, ):
                        if context.unsupported_object_callback:
                            context.unsupported_object_callback('Perpendicular line labels are not supported by QGIS')

                        dest_label_settings.placement = QgsPalLayerSettings.Line
                        placement_flags = QgsPalLayerSettings.OnLine | QgsPalLayerSettings.MapOrientation
                    elif maplex_overposter.line_placement_method in (MaplexOverposterLayerProperties.LINE_PLACEMENT_OFFSET_HORIZONTAL_FROM_LINE, ):
                        dest_label_settings.placement = QgsPalLayerSettings.Horizontal
                        placement_flags = QgsPalLayerSettings.AboveLine | QgsPalLayerSettings.MapOrientation
                    elif maplex_overposter.line_placement_method in (MaplexOverposterLayerProperties.LINE_PLACEMENT_OFFSET_STRAIGHT_FROM_LINE, ):
                        dest_label_settings.placement = QgsPalLayerSettings.Line
                        placement_flags = QgsPalLayerSettings.AboveLine | QgsPalLayerSettings.MapOrientation
                    elif maplex_overposter.line_placement_method in (MaplexOverposterLayerProperties.LINE_PLACEMENT_OFFSET_CURVED_FROM_LINE, ):
                        dest_label_settings.placement = QgsPalLayerSettings.Curved
                        placement_flags = QgsPalLayerSettings.AboveLine | QgsPalLayerSettings.MapOrientation
                    elif maplex_overposter.line_placement_method in (MaplexOverposterLayerProperties.LINE_PLACEMENT_OFFSET_PERPENDICULAR_FROM_LINE, ):
                        if context.unsupported_object_callback:
                            context.unsupported_object_callback('Perpendicular line labels are not supported by QGIS')

                        dest_label_settings.placement = QgsPalLayerSettings.Line
                        placement_flags = QgsPalLayerSettings.AboveLine | QgsPalLayerSettings.MapOrientation

            dest_label_settings.placementFlags = placement_flags
            # NOT supported:
            # at start/at end
            # perpendicular
            # before/after distance

        else:
            dest_label_settings.placement = QgsPalLayerSettings.Horizontal
            dest_label_settings.multilineAlign = QgsPalLayerSettings.MultiCenter

        # label_settings.placementFlags
        # label_settings.centroidWhole
        # label_settings.centroidInside
        # label_settings.fitInPolygonOnly

        if overposter:
            if False:  # pylint: disable=using-constant-test
                dest_label_settings.dist = overposter.line_offset or 0
            else:
                dest_label_settings.dist = overposter.offset

        dest_label_settings.distUnits = QgsUnitTypes.RenderPoints
        dest_label_settings.offsetType = QgsPalLayerSettings.FromSymbolBounds

        # label_settings.repeatDistance
        # label_settings.repeatDistanceUnit
        # label_settings.quadOffset
        # label_settings.xOffset
        # label_settings.yOffset
        # label_settings.offsetUnits
        # label_settings.angleOffset

        try:
            dest_label_settings.priority = LabelConverter.LABEL_WEIGHT_MAP[overposter.label_weight]
        except AttributeError:
            # maplex -- where is this?
            pass

        # label_settings.displayAll
        # label_settings.upsidedownLabels

        dest_label_settings.labelPerPart = False
        if False:  # pylint: disable=using-constant-test
            pass
        else:
            try:
                dest_label_settings.labelPerPart = overposter.number_restriction == BasicOverposterLayerProperties.NUM_ONE_PER_PART
            except AttributeError:
                pass  # TODO - maplex

        # label_settings.mergeLines

        if overposter:
            try:
                dest_label_settings.obstacleFactor = LabelConverter.OBSTACLE_WEIGHT_MAP[overposter.feature_weight]
            except KeyError:
                # maplex
                if overposter.feature_weight is not None:
                    dest_label_settings.obstacleFactor = overposter.feature_weight / 250.0

        if isinstance(maplex_overposter, MaplexOverposterLayerProperties):
            if maplex_overposter.rotation_properties.rotate_by_attribute:
                if maplex_overposter.rotation_properties.rotation_type == MaplexRotationProperties.ROTATE_LABEL_ARITHMETIC:
                    rotation_expression = '-"{}"'.format(maplex_overposter.rotation_properties.rotation_attribute)
                    dd = dest_label_settings.dataDefinedProperties()
                    dd.setProperty(QgsPalLayerSettings.LabelRotation, QgsProperty.fromExpression(rotation_expression))
                    dest_label_settings.setDataDefinedProperties(dd)
                elif maplex_overposter.rotation_properties.rotation_type == MaplexRotationProperties.ROTATE_LABEL_GEOGRAPHIC:
                    dd = dest_label_settings.dataDefinedProperties()
                    dd.setProperty(QgsPalLayerSettings.LabelRotation,
                                   QgsProperty.fromField(maplex_overposter.rotation_properties.rotation_attribute))
                    dest_label_settings.setDataDefinedProperties(dd)

        if overposter:
            dest_label_settings.obstacle = overposter.feature_weight not in (BasicOverposterLayerProperties.WEIGHT_NONE,)
        # label_settings.obstacleType

    @staticmethod
    def convert_label_style(properties: LabelStyle, context) -> QgsPalLayerSettings:
        """
        Converts a LabelStyle to QGIS equivalent
        """
        label_settings = QgsPalLayerSettings()
        label_settings.drawLabels = True

        LabelConverter.convert_label_text_symbol(properties.text_symbol, label_settings, context)
        LabelConverter.convert_overposter(properties.overposter, properties.overposter if isinstance(properties.overposter, MaplexOverposterLayerProperties) else None, QgsWkbTypes.UnknownGeometry, label_settings, context)

        label_settings.layerType = QgsWkbTypes.PointGeometry
        return label_settings

    @staticmethod
    def convert_label_engine_layer_properties(properties: LabelEngineLayerProperties, layer_geometry_type,
                                              context) -> QgsPalLayerSettings:
        """
        Converts LabelEngineLayerProperties to QGIS equivalent
        """
        label_settings = QgsPalLayerSettings()
        label_settings.drawLabels = properties.label_features

        if isinstance(properties, (LabelEngineLayerProperties, MaplexLabelEngineLayerProperties)):
            LabelConverter.convert_label_text_symbol(properties.text_symbol, label_settings, context)
        else:
            LabelConverter.convert_label_text_symbol(properties.text_symbol.symbol, label_settings, context)

        label_settings.fieldName = ExpressionConverter.convert(properties.expression, properties.expression_parser,
                                                               False if False else properties.advanced_expression, context)  # pylint: disable=using-constant-test
        label_settings.isExpression = True

        if False:  # pylint: disable=using-constant-test
            pass
        else:
            LabelConverter.convert_overposter(properties.overposter,
                                              properties.overposter if isinstance(properties.overposter, MaplexOverposterLayerProperties) else None,
                                              layer_geometry_type, label_settings, context)

        label_settings.scaleVisibility = bool(properties.scale_range_max or properties.scale_range_min)
        # layer.zoom_max = "don't show when zoomed out beyond"
        zoom_max = properties.scale_range_max or 0
        # layer.zoom_min = "don't show when zoomed in beyond"
        zoom_min = properties.scale_range_min or 0
        if zoom_max and zoom_min and zoom_min > zoom_max:
            # inconsistent scale range -- zoom_max should be bigger number than zoom_min
            zoom_min, zoom_max = zoom_max, zoom_min

        # qgis maximum scale = don't show when zoomed in beyond, i.e. ArcGIS zoom_min
        label_settings.maximumScale = zoom_min
        # qgis minimum scale = don't show when zoomed out beyond, i.e. ArcGIS zoom_max
        label_settings.minimumScale = zoom_max

        return label_settings

    @staticmethod
    def convert_callout(callout, context, reference_scale=None):
        """
        Converts a callout
        """
        if isinstance(callout, MarkerTextBackground):
            # not a callout
            return None
        elif isinstance(callout, SimpleLineCallout):
            return LabelConverter.convert_simple_line_callout(callout, context, reference_scale)
        elif isinstance(callout, LineCallout):
            return LabelConverter.convert_line_callout(callout, context, reference_scale)
        elif isinstance(callout, BalloonCallout):
            return LabelConverter.convert_balloon_callout(callout, context, reference_scale)
        else:
            raise NotImplementedException('Converting {} not implemented yet'.format(callout.__class__.__name__))

    @staticmethod
    def convert_simple_line_callout(callout: SimpleLineCallout, context,
                                    reference_scale=None):  # pylint: disable=unused-argument
        """
        Converts a SimpleLineCallout
        """
        try:
            from qgis.core import QgsSimpleLineCallout  # pylint: disable=import-outside-toplevel
        except ImportError:
            # raise UnreadableSymbolException('Converting callouts requires QGIS 3.10 or later')
            return None

        from .symbols import SymbolConverter  # pylint: disable=import-outside-toplevel

        res = QgsSimpleLineCallout()
        symbol = SymbolConverter.Symbol_to_QgsSymbol(callout.line_symbol, context)
        res.setLineSymbol(symbol)

        res.setEnabled(True)

        res.setMinimumLength(context.convert_size(callout.tolerance))
        res.setMinimumLengthUnit(context.units)

        return res

    @staticmethod
    def convert_line_callout(callout: LineCallout, context, reference_scale=None):
        """
        Converts a LineCallout
        """
        try:
            from qgis.core import QgsSimpleLineCallout, \
                QgsManhattanLineCallout  # pylint: disable=import-outside-toplevel
        except ImportError:
            if context.unsupported_object_callback:
                context.unsupported_object_callback('Converting callouts requires QGIS 3.10 or later')
            return None

        if callout.accent_symbol and context.unsupported_object_callback:
            context.unsupported_object_callback('Callout accent symbols are not supported by QGIS')
        if callout.border_symbol and context.unsupported_object_callback:
            context.unsupported_object_callback('Callout border symbols are not supported by QGIS')

        from .symbols import SymbolConverter  # pylint: disable=import-outside-toplevel

        if callout.style == LineCallout.STYLE_BASE:
            res = QgsManhattanLineCallout()
        elif callout.style == LineCallout.STYLE_MIDPOINT:
            res = QgsSimpleLineCallout()
        else:
            # raise NotImplementedException('QGIS has no support for {} callout styles'.format(LineCallout.style_to_string(callout.style)))
            res = QgsSimpleLineCallout()

        if not callout.leader_symbol:
            return None

        symbol = SymbolConverter.Symbol_to_QgsSymbol(callout.leader_symbol, context)

        # qgis renders these lines in the opposite direction to Arc!
        symbol = SymbolConverter.reverse_line_symbol(symbol)

        if reference_scale:
            symbol.setOutputUnit(QgsUnitTypes.RenderMetersInMapUnits)
            if context.units == QgsUnitTypes.RenderMillimeters:
                symbol.setWidth(symbol.width() * reference_scale * 0.001)
            else:
                symbol.setWidth(symbol.width() * reference_scale * 0.000352778)
        res.setLineSymbol(symbol)

        res.setEnabled(True)

        res.setMinimumLength(context.convert_size(callout.tolerance))
        res.setMinimumLengthUnit(context.units)

        # GAP - is this from the label or the feature??
        # margins -- is this from the label?

        return res

    @staticmethod
    def convert_balloon_callout(callout: BalloonCallout, context,
                                reference_scale=None):  # pylint: disable=unused-argument
        """
        Converts a BalloonCallout
        """
        try:
            from qgis.core import QgsBalloonCallout  # pylint: disable=import-outside-toplevel
        except ImportError:
            if context.unsupported_object_callback:
                context.unsupported_object_callback('Converting balloon callouts requires QGIS 3.20 or later')
            return None

        if callout.style == BalloonCallout.STYLE_OVAL and context.unsupported_object_callback:
            context.unsupported_object_callback('Oval style balloon callouts are not supported by QGIS')
            return None

        from .symbols import SymbolConverter  # pylint: disable=import-outside-toplevel,cyclic-import
        res = QgsBalloonCallout()

        if not callout.fill_symbol:
            return None

        symbol = SymbolConverter.Symbol_to_QgsSymbol(callout.fill_symbol, context)
        res.setFillSymbol(symbol)
        res.setEnabled(True)
        res.setWedgeWidth(context.convert_size(5.6))
        res.setWedgeWidthUnit(context.units)

        if callout.style == BalloonCallout.STYLE_ROUNDED_RECTANGLE:
            res.setCornerRadius(context.convert_size(5.6))
            res.setCornerRadiusUnit(context.units)

        margin_left = context.convert_size(callout.margin_left)
        margin_right = context.convert_size(callout.margin_right)
        margin_top = context.convert_size(callout.margin_top)
        margin_bottom = context.convert_size(callout.margin_bottom)
        res.setMargins(QgsMargins(margin_left, margin_top, margin_right, margin_bottom))
        res.setMarginsUnit(context.units)

        return res

    @staticmethod
    def convert_fdo_annotations(dest_layer: QgsVectorLayer, context):  # pylint: disable=unused-argument
        """
        Converts FDO annotations
        """
        # one label class, use simple labeling
        label_settings = QgsPalLayerSettings()
        label_settings.fieldName = 'TextString'
        label_settings.drawLabels = True
        label_settings.placement = QgsPalLayerSettings.OverPoint
        label_settings.dataDefinedProperties().setProperty(QgsPalLayerSettings.Family,
                                                           QgsProperty.fromField('FontName'))
        label_settings.dataDefinedProperties().setProperty(QgsPalLayerSettings.Size,
                                                           QgsProperty.fromField('FontSize'))
        label_settings.dataDefinedProperties().setProperty(QgsPalLayerSettings.Bold,
                                                           QgsProperty.fromField('Bold'))
        label_settings.dataDefinedProperties().setProperty(QgsPalLayerSettings.Italic,
                                                           QgsProperty.fromField('Italic'))
        label_settings.dataDefinedProperties().setProperty(QgsPalLayerSettings.Underline,
                                                           QgsProperty.fromField('Underline'))

        quadrant_property = QgsProperty.fromExpression("""case
    when  "VerticalAlignment" = 0 then -- top
    case
        when  "HorizontalAlignment" = 0 then 0
        when  "HorizontalAlignment" = 1 then 1
        when  "HorizontalAlignment" = 2 then 2
    end

    when  "VerticalAlignment" = 1 then -- center
    case
        when  "HorizontalAlignment" = 0 then 3
        when  "HorizontalAlignment" = 1 then 4
        when  "HorizontalAlignment" = 2 then 5
    end

    when  "VerticalAlignment" in (2,3) then -- baseline, bottom
    case
        when  "HorizontalAlignment" = 0 then 6
        when  "HorizontalAlignment" = 1 then 7
        when  "HorizontalAlignment" = 2 then 8
    end
end""")
        label_settings.dataDefinedProperties().setProperty(QgsPalLayerSettings.OffsetQuad, quadrant_property)
        label_settings.dataDefinedProperties().setProperty(QgsPalLayerSettings.LabelRotation,
                                                           QgsProperty.fromExpression('360-"Angle"'))
        label_settings.dataDefinedProperties().setProperty(QgsPalLayerSettings.OffsetXY,
                                                           QgsProperty.fromExpression(
                                                               ' concat(  "XOffset" ,\',\', "YOffset" )'))

        labeling = QgsVectorLayerSimpleLabeling(label_settings)
        dest_layer.setLabeling(labeling)


if Qgis.QGIS_VERSION_INT > 31600:
    LabelConverter.TEXT_ALIGN_MAP[TextSymbol.HALIGN_FULL] = QgsPalLayerSettings.MultiJustify
