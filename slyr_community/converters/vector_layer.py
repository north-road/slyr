#!/usr/bin/env python

# /***************************************************************************
# vector_layer.py
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
Converts vector layer to QGIS vector layer
"""

import os
from pathlib import Path
from typing import Union

from qgis.core import (
    Qgis,
    QgsCoordinateReferenceSystem,
    QgsWkbTypes,
    QgsVectorLayer,
    QgsVectorLayerJoinInfo,
    QgsNullSymbolRenderer,
    QgsMapLayerLegend,
    QgsRuleBasedRenderer,
    QgsSingleSymbolRenderer,
    QgsAction,
    QgsExpression,
    QgsMapLayer,
    QgsProviderRegistry,
    QgsAttributeTableConfig,
    QgsEditorWidgetSetup,
)

from .context import Context
from .crs import CrsConverter
from .dataset_name import DatasetNameConverter, DataSourceProperties
from .diagrams import DiagramConverter
from .expressions import ExpressionConverter
from .labels import LabelConverter
from .vector_renderer import VectorRendererConverter

from ..parser.objects import (
    FDOGraphicsLayer,
    FeatureLayer,
    Geometry,
    MemoryRelationshipClassName,
    RelQueryTableName,
    StandaloneTable,
)


class VectorLayerConverter:
    """
    Converts vector layers
    """

    @staticmethod
    def geometry_type_to_wkb(geometry_type):
        """
        Converts ESRI geometry type to WKB equivalent
        """
        GEOMETRY_TYPES = {
            0: QgsWkbTypes.Type.NoGeometry,
            1: QgsWkbTypes.Type.Point,
            2: QgsWkbTypes.Type.MultiPoint,
            3: QgsWkbTypes.Type.MultiLineString,
            4: QgsWkbTypes.Type.MultiPolygon,
            5: QgsWkbTypes.Type.MultiPolygon,
            6: QgsWkbTypes.Type.MultiLineString,
            7: QgsWkbTypes.Type.Unknown,
            9: QgsWkbTypes.Type.MultiPolygon,
            11: QgsWkbTypes.Type.MultiLineString,
            13: QgsWkbTypes.Type.MultiLineString,
            14: QgsWkbTypes.Type.CircularString,
            15: QgsWkbTypes.Type.Unknown,
            16: QgsWkbTypes.Type.Unknown,
            17: QgsWkbTypes.Type.Unknown,
            18: QgsWkbTypes.Type.Unknown,
            19: QgsWkbTypes.Type.Unknown,
            20: QgsWkbTypes.Type.Unknown,
            21: QgsWkbTypes.Type.Unknown,
            22: QgsWkbTypes.Type.Unknown,
        }
        return GEOMETRY_TYPES[geometry_type]

    @staticmethod
    def layer_to_wkb_type(layer):
        """
        Tries to determine the WKB type for an ESRI layer
        """
        # work out WKB type
        if hasattr(layer, "shape_type") and layer.shape_type != Geometry.GEOMETRY_ANY:
            return VectorLayerConverter.geometry_type_to_wkb(layer.shape_type)
        elif (
            hasattr(layer, "datasource_type")
            and layer.datasource_type == "XY Event Source"
        ):
            return QgsWkbTypes.Type.Point
        elif (
            hasattr(layer, "dataset_name")
            and hasattr(layer.dataset_name, "shape_type")
            and layer.dataset_name.shape_type == 0
        ):
            # not stored in lyr, guess from renderer
            return VectorRendererConverter.guess_geometry_type_from_renderer(layer)
        elif hasattr(layer, "dataset_name") and hasattr(
            layer.dataset_name, "shape_type"
        ):
            return VectorLayerConverter.geometry_type_to_wkb(
                layer.dataset_name.shape_type
            )
        return QgsWkbTypes.Type.Unknown

    @staticmethod
    def layer_to_QgsVectorLayer(
        source_layer,  # pylint: disable=too-many-locals,too-many-branches,too-many-statements
        input_file: str,
        context: Context,
        fallback_crs=QgsCoordinateReferenceSystem(),
    ):
        """
        Converts a vector layer
        """
        if source_layer.__class__.__name__ == "CadFeatureLayer":
            layer = source_layer.layer
        else:
            layer = source_layer

        context.document_file = input_file

        context.field_to_alias_map = {}
        for field, info in layer.field_info.items():
            if info and field != info.alias:
                context.field_to_alias_map[field] = info.alias

        crs = (
            CrsConverter.convert_crs(layer.layer_extent.crs, context)
            if layer.layer_extent
            else QgsCoordinateReferenceSystem()
        )
        if not crs.isValid():
            crs = fallback_crs

        subset_string = ""
        if layer.selection_set:
            subset_string = "fid in ({})".format(
                ",".join([str(s) for s in layer.selection_set])
            )
        elif layer.definition_query:
            subset_string = ExpressionConverter.convert_esri_sql(layer.definition_query)

        base, _ = os.path.split(input_file)

        wkb_type_hint = VectorLayerConverter.layer_to_wkb_type(layer)

        uri, wkb_type, provider, encoding, file_name = VectorLayerConverter.get_uri(
            source_layer=source_layer,
            obj=layer,
            base=base,
            crs=crs,
            subset=subset_string,
            context=context,
            input_file=input_file,
            wkb_type_hint=wkb_type_hint,
        )

        if wkb_type is None or wkb_type in (
            QgsWkbTypes.Type.Unknown,
            QgsWkbTypes.Type.GeometryCollection,
        ):
            wkb_type = VectorLayerConverter.layer_to_wkb_type(layer)
        elif wkb_type == QgsWkbTypes.Type.NoGeometry and source_layer.shape_type != 0:
            wkb_type = VectorLayerConverter.layer_to_wkb_type(layer)

        context.layer_type_hint = wkb_type

        # try to get the layer name so that we can remove it from field references.
        # e.g. if layer name is polys then qgis won't support to arcgis style "polys.field" format
        parts = QgsProviderRegistry.instance().decodeUri(provider, uri)
        context.main_layer_name = parts.get("layerName")
        if not context.main_layer_name and provider == "ogr":
            context.main_layer_name = Path(parts["path"]).stem

        if context.main_layer_name:
            subset_string = subset_string.replace(context.main_layer_name + ".", "")

        opts = QgsVectorLayer.LayerOptions()
        if wkb_type is not None:
            opts.fallbackWkbType = wkb_type

        if provider == "ogr" and subset_string:
            if ".dxf" in uri.lower():
                context.push_warning("Filtering DXF layers is not supported in QGIS")
            else:
                uri += "|subset={}".format(subset_string)

        original_uri = uri
        if context.defer_set_path_for_mdb_layers and ".mdb" in uri.lower():
            uri = "xxxxxxxxx" + uri

        vl = QgsVectorLayer(uri, layer.name, provider, opts)
        if context.defer_set_path_for_mdb_layers:
            vl.setCustomProperty("original_uri", original_uri)

        if layer.renderer:
            renderer = VectorRendererConverter.convert_renderer(
                layer.renderer, layer, context, vl
            )
            try:
                if not renderer.usingSymbolLevels():
                    renderer.setUsingSymbolLevels(layer.use_advanced_symbol_levels)
            except AttributeError:
                pass

            page_filter_expression = None
            if layer.use_page_definition_query:
                page_filter_expression = '"{}" {} @atlas_pagename'.format(
                    layer.page_name_field, layer.page_name_match_operator
                )

            if page_filter_expression:
                root_rule = QgsRuleBasedRenderer.Rule(None)

                # special case -- convert a simple renderer
                if isinstance(renderer, QgsSingleSymbolRenderer):
                    filter_rule = QgsRuleBasedRenderer.Rule(renderer.symbol().clone())
                    filter_rule.setFilterExpression(page_filter_expression)
                    filter_rule.setLabel(layer.name)
                    filter_rule.setDescription(layer.name)
                    root_rule.appendChild(filter_rule)
                else:
                    source_rule_renderer = QgsRuleBasedRenderer.convertFromRenderer(
                        renderer
                    )
                    filter_rule = QgsRuleBasedRenderer.Rule(None)
                    filter_rule.setFilterExpression(page_filter_expression)
                    filter_rule.setLabel("Current Atlas Page")
                    filter_rule.setDescription("Current Atlas Page")
                    root_rule.appendChild(filter_rule)
                    for child in source_rule_renderer.rootRule().children():
                        filter_rule.appendChild(child.clone())

                renderer = QgsRuleBasedRenderer(root_rule)

            if renderer:
                vl.setRenderer(renderer)
                vl.triggerRepaint()
        else:
            vl.setRenderer(QgsNullSymbolRenderer())
            vl.triggerRepaint()

        # layer.zoom_max = "don't show when zoomed out beyond"
        zoom_max = layer.zoom_max
        # layer.zoom_min = "don't show when zoomed in beyond"
        zoom_min = layer.zoom_min

        enabled_scale_range = bool(zoom_max or zoom_min)
        if zoom_max and zoom_min and zoom_min > zoom_max:
            # inconsistent scale range -- zoom_max should be bigger number than zoom_min
            zoom_min, zoom_max = zoom_max, zoom_min
        # qgis minimum scale = don't show when zoomed out beyond, i.e. ArcGIS zoom_max
        vl.setMinimumScale(zoom_max if enabled_scale_range else layer.stored_zoom_max)
        # qgis maximum scale = don't show when zoomed in beyond, i.e. ArcGIS zoom_min
        vl.setMaximumScale(zoom_min if enabled_scale_range else layer.stored_zoom_min)
        vl.setScaleBasedVisibility(enabled_scale_range)

        vl.setOpacity(1.0 - (layer.transparency or 0) / 100)

        has_set_display_expression = False
        if (
            layer.display_expression_properties
            and layer.display_expression_properties.expression
            and layer.display_expression_properties.expression_parser is not None
        ):
            has_set_display_expression = True
            vl.setDisplayExpression(
                ExpressionConverter.convert(
                    layer.display_expression_properties.expression,
                    layer.display_expression_properties.expression_parser,
                    layer.display_expression_properties.advanced,
                    context,
                )
            )

        if encoding:
            vl.dataProvider().setEncoding(encoding)

        if subset_string:
            vl.setSubsetString(subset_string)

        vl.setCrs(crs)

        for e in layer.extensions:
            if e.__class__.__name__ == "ServerLayerExtension":
                if "CopyrightText" in e.properties.properties:
                    layer_credits = e.properties.properties["CopyrightText"]
                    metadata = vl.metadata()
                    rights = metadata.rights()
                    rights.append(layer_credits)
                    metadata.setRights(rights)
                    vl.setMetadata(metadata)

        metadata = vl.metadata()
        metadata.setAbstract(layer.description)
        vl.setMetadata(metadata)

        if True:
            LabelConverter.convert_annotation_collection(
                layer.annotation_collection,
                source_layer=layer,
                dest_layer=vl,
                context=context,
            )
            vl.setLabelsEnabled(layer.labels_enabled)

        DiagramConverter.convert_diagrams(
            layer.renderer, dest_layer=vl, context=context
        )

        join_layer = VectorLayerConverter.add_joined_layer(
            source_layer=layer, input_file=input_file, base_layer=vl, context=context
        )

        context.dataset_name = ""

        vl.setLegend(QgsMapLayerLegend.defaultVectorLegend(vl))

        if layer.hyperlinks:
            VectorLayerConverter.convert_hyperlinks(layer.hyperlinks, vl)

        if not has_set_display_expression:
            vl.setDisplayExpression(QgsExpression.quotedColumnRef(layer.display_field))

        res = [vl]
        if join_layer:
            res.append(join_layer)

        hidden_field_names = set()
        hidden_field_indices = []
        attribute_table_config = vl.attributeTableConfig()
        columns = []
        edit_form_config = vl.editFormConfig()
        for field, info in layer.field_info.items():
            column_config = QgsAttributeTableConfig.ColumnConfig()
            column_config.name = field

            if not info:
                columns.append(column_config)
                continue

            field_index = vl.fields().lookupField(field)
            if field_index >= 0:
                if field != info.alias:
                    vl.setFieldAlias(field_index, info.alias)
                if not info.visible:
                    widget_setup = QgsEditorWidgetSetup("Hidden", {})
                    vl.setEditorWidgetSetup(field_index, widget_setup)
                if info.read_only:
                    edit_form_config.setReadOnly(field_index, True)
            column_config.hidden = not info.visible
            if column_config.hidden:
                if field_index >= 0:
                    hidden_field_indices.append(field_index)
                hidden_field_names.add(field)

            columns.append(column_config)

        attribute_table_config.setColumns(columns)
        vl.setAttributeTableConfig(attribute_table_config)
        vl.setEditFormConfig(edit_form_config)

        if Qgis.QGIS_VERSION_INT >= 33400:
            for index in hidden_field_indices:
                vl.setFieldConfigurationFlag(
                    index, Qgis.FieldConfigurationFlag.HideFromWms, True
                )
                vl.setFieldConfigurationFlag(
                    index, Qgis.FieldConfigurationFlag.HideFromWfs, True
                )
        else:
            vl.setExcludeAttributesWfs(hidden_field_names)
            vl.setExcludeAttributesWms(hidden_field_names)

        context.main_layer_name = None
        return res

    # pylint: disable=too-many-locals,too-many-branches
    @staticmethod
    def standalone_table_to_QgsVectorLayer(
        layer: StandaloneTable,
        input_file: str,
        context: Context,
    ):
        """
        Converts a standalone table to a vector layer
        """
        subset_string = ""
        if layer.definition_query:
            subset_string = ExpressionConverter.convert_esri_sql(layer.definition_query)

        base, _ = os.path.split(input_file)

        uri, wkb_type, provider, encoding, file_name = VectorLayerConverter.get_uri(
            source_layer=layer,
            obj=layer,
            base=base,
            crs=QgsCoordinateReferenceSystem(),
            subset=subset_string,
            context=context,
            input_file=input_file,
            wkb_type_hint=QgsWkbTypes.Type.NoGeometry,
        )

        if wkb_type is None:
            wkb_type = QgsWkbTypes.Type.NoGeometry
        context.layer_type_hint = wkb_type

        opts = QgsVectorLayer.LayerOptions()
        if wkb_type is not None:
            opts.fallbackWkbType = wkb_type

        if provider == "ogr" and subset_string:
            uri += "|subset={}".format(subset_string)

        vl = QgsVectorLayer(uri, layer.name, provider, opts)

        metadata = vl.metadata()
        metadata.setAbstract(layer.description)
        vl.setMetadata(metadata)  #

        if encoding:
            vl.dataProvider().setEncoding(encoding)

        if subset_string:
            vl.setSubsetString(subset_string)

        for e in layer.extensions:
            if e.__class__.__name__ == "ServerLayerExtension":
                if "CopyrightText" in e.properties.properties:
                    layer_credits = e.properties.properties["CopyrightText"]
                    metadata = vl.metadata()
                    rights = metadata.rights()
                    rights.append(layer_credits)
                    metadata.setRights(rights)
                    vl.setMetadata(metadata)

        # setup joins
        join_layer = None
        join_layer = VectorLayerConverter.add_joined_layer(
            source_layer=layer,
            input_file=input_file,
            base_layer=vl,
            context=context,
        )

        context.dataset_name = ""

        vl.setLegend(QgsMapLayerLegend.defaultVectorLegend(vl))

        res = [vl]
        if join_layer:
            res.append(join_layer)

        return res

    # pylint: enable=too-many-locals,too-many-branches

    @staticmethod
    def convert_hyperlinks(hyperlinks, layer: QgsVectorLayer):
        """
        Converts hyperlinks to QGIS actions
        """
        script = """from qgis.PyQt.QtWidgets import QMessageBox, QInputDialog
    from qgis.PyQt.QtGui import QDesktopServices
    from qgis.PyQt.QtCore import QUrl

    hyperlinks = {
    """

        features = {}
        for h in hyperlinks:
            if h.feature_id not in features:
                features[h.feature_id] = []
            features[h.feature_id].append(h.url)

        for _id, links in features.items():
            script += f""" {_id}: ['{"','".join(links)}'],\n"""

        script += """}

    if [% $id %] in hyperlinks:
        res, ok = QInputDialog.getItem(None, 'Hyperlinks', '', hyperlinks[[% $id %]],0,False)
        if ok:
            QDesktopServices.openUrl(QUrl(res))
    """
        action = QgsAction(
            QgsAction.ActionType.GenericPython,
            "Open Hyperlinks",
            script,
            "",
            False,
            "Hyperlinks",
            {"Field", "Feature", "Layer", "Canvas"},
        )
        layer.actions().addAction(action)

    # pylint: disable=too-many-branches
    @staticmethod
    def add_joined_layer(
        source_layer: Union[FeatureLayer, StandaloneTable],
        input_file: str,
        base_layer: QgsVectorLayer,
        context: Context,
    ):
        """
        Adds joined layers
        """
        if not source_layer.join:
            return None

        join_info = QgsVectorLayerJoinInfo()

        if isinstance(source_layer.join, MemoryRelationshipClassName):
            if isinstance(source_layer.join.origin_name, RelQueryTableName):
                context.push_warning(
                    "Nested joins are not supported in QGIS", level=Context.CRITICAL
                )

                return None

            join_info.setJoinFieldName(source_layer.join.origin_primary_key)
            join_info.setTargetFieldName(source_layer.join.origin_foreign_key)

            base, _ = os.path.split(input_file)

            source_layer_props = DatasetNameConverter.convert(
                name=source_layer.join.destination_name,
                base=base,
                crs=QgsCoordinateReferenceSystem(),
                context=context,
            )
            context.layer_type_hint = source_layer_props.wkb_type

            name = "join"
            if hasattr(source_layer.join.destination_name, "name"):
                name = source_layer.join.destination_name.name
                join_info.setPrefix(name + ".")

            opts = QgsVectorLayer.LayerOptions()
            if source_layer_props.wkb_type is not None:
                opts.fallbackWkbType = source_layer_props.wkb_type

            vl = QgsVectorLayer(
                source_layer_props.uri, name, source_layer_props.provider, opts
            )

            # todo layer name
            vl.setRenderer(QgsNullSymbolRenderer())

            try:
                vl.setFlags(vl.flags() | QgsMapLayer.LayerFlag.Private)
            except AttributeError:
                pass

            join_info.setJoinLayer(vl)
            base_layer.addJoin(join_info)

            return vl

        else:
            context.push_warning(
                "Join layers of type {} are not yet supported".format(
                    source_layer.join.__class__.__name__
                ),
                level=Context.CRITICAL,
            )

            return None

    # pylint: enable=too-many-branches

    @staticmethod
    def get_uri(
        source_layer,
        obj,
        base: str,
        subset: str,
        crs: QgsCoordinateReferenceSystem,
        context: Context,
        input_file: str,
        wkb_type_hint: QgsWkbTypes.Type = QgsWkbTypes.Type.Unknown,
    ):
        """
        Gets the URI for a converted layer
        """
        if (
            source_layer.__class__.__name__ == "CadFeatureLayer"
            and source_layer.drawing_object
        ):
            source_props = DataSourceProperties(
                uri=source_layer.drawing_object.path,
                file_name=source_layer.drawing_object.path,
                encoding=None,
                provider="ogr",
                wkb_type=None,
            )
        else:
            if obj.dataset_name is None:
                context.push_warning(
                    "Layer has a corrupted path in MXD document -- the path cannot be recovered",
                    level=Context.CRITICAL,
                )

            source_props = DatasetNameConverter.convert(
                name=obj.dataset_name,
                base=base,
                crs=crs,
                subset=subset,
                context=context,
                document_file=input_file,
                wkb_type_hint=wkb_type_hint,
            )

        return (
            source_props.uri,
            source_props.wkb_type,
            source_props.provider,
            source_props.encoding,
            source_props.file_name,
        )

    @staticmethod
    def source_to_QgsVectorLayer(source, name, input_file, context: Context):
        """
        Converts a source path to a vector layer
        """
        base, _ = os.path.split(input_file)

        source_props = DatasetNameConverter.convert(
            name=source,
            base=base,
            crs=QgsCoordinateReferenceSystem(),
            subset=None,
            context=context,
            document_file=input_file,
        )

        context.layer_type_hint = source_props.wkb_type

        opts = QgsVectorLayer.LayerOptions()
        if source_props.wkb_type is not None:
            opts.fallbackWkbType = source_props.wkb_type

        return QgsVectorLayer(source_props.uri, name, source_props.provider, opts)
