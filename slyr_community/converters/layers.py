#!/usr/bin/env python

# /***************************************************************************
# layers.py
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
Converts layers to QGIS layers
"""

#  pylint: disable=too-many-lines

import os
from typing import Tuple, Optional

from qgis.PyQt.QtCore import (
    QFile,
    QTextStream
)
from qgis.PyQt.QtXml import QDomDocument
from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsLayerTreeGroup,
    QgsLayerDefinition,
    QgsFileUtils,
    QgsReadWriteContext,
    QgsPathResolver
)

from .context import Context
from .converter import NotImplementedException
from .raster_layer import RasterLayerConverter
from .vector_layer import VectorLayerConverter
from ..parser.objects.base_map_layer import BaseMapLayer
from ..parser.objects.cad_annotation_layer import CadAnnotationLayer
from ..parser.objects.cad_feature_layer import CadFeatureLayer
from ..parser.objects.cad_layer import CadLayer
from ..parser.objects.feature_class_name import (
    FgdbFeatureClassName,
    FeatureClassName
)
from ..parser.objects.feature_layer import FeatureLayer
from ..parser.objects.group_layer import GroupLayer
from ..parser.objects.image_server_layer import ImageServerLayer
from ..parser.objects.internet_tiled_layer import InternetTiledLayer
from ..parser.objects.las_dataset_layer import LasDatasetLayer
from ..parser.objects.map_server_layer import MapServerLayer, \
    MapServerSubLayer, MapServerBasicSublayer
from ..parser.objects.map_server_rest_layer import MapServerRESTLayer, \
    MapServerRESTSubLayer
from ..parser.objects.network_layer import NetworkLayer
from ..parser.objects.raster_basemap_layer import RasterBasemapLayer
from ..parser.objects.raster_catalog_layer import RasterCatalogLayer
from ..parser.objects.raster_layer import RasterLayer
from ..parser.objects.standalone_table import StandaloneTable
from ..parser.objects.tin_layer import TinLayer
from ..parser.objects.topology_layer import TopologyLayer
from ..parser.objects.wms_layer import WmsMapLayer, WmsLayer
from ..parser.objects.wmts_layer import WmtsLayer


class LayerConverter:
    """
    Layer converter
    """

    # pylint: disable=too-many-branches, too-many-statements
    @staticmethod
    def layer_to_QgsLayer(source_layer,
                          input_file,
                          context: Context,
                          fallback_crs=QgsCoordinateReferenceSystem(),
                          defer_layer_uri_set: bool = False):
        """
        Converts a layer to a QGIS layer
        """

        if isinstance(source_layer, CadAnnotationLayer):
            source_layer = source_layer.coverage_layer

        context.layer_name = source_layer.name
        res = []
        if LayerConverter.is_vector_layer(source_layer):
            try:
                res = VectorLayerConverter.layer_to_QgsVectorLayer(
                    source_layer, input_file,
                    context=context,
                    fallback_crs=fallback_crs,
                    defer_layer_uri_set=defer_layer_uri_set)
            except NotImplementedException as e:
                context.push_warning(
                    'Layer “{}” has been removed: {}'.format(
                        source_layer.name, e), level=Context.CRITICAL)

        elif isinstance(source_layer, (RasterLayer,)):
            res = [RasterLayerConverter.raster_layer_to_QgsRasterLayer(
                source_layer, input_file, context=context,
                fallback_crs=fallback_crs)]
        elif isinstance(source_layer, (WmsMapLayer,)):
            pass
        elif isinstance(source_layer, WmtsLayer):
            pass
        elif isinstance(source_layer, RasterBasemapLayer):
            res = RasterLayerConverter.raster_basemap_layer_to_QgsRasterLayer(
                source_layer, input_file, context=context,
                fallback_crs=fallback_crs)
        elif isinstance(source_layer, (MapServerLayer,)):
            pass
        elif isinstance(source_layer, InternetTiledLayer):
            pass
        elif False:  # pylint: disable=using-constant-test
            pass
        elif isinstance(source_layer, MapServerRESTLayer):
            pass
        elif isinstance(source_layer, StandaloneTable):
            res = VectorLayerConverter.standalone_table_to_QgsVectorLayer(
                source_layer, input_file, context=context)
        elif isinstance(source_layer, (TinLayer,)):
            pass
        elif False:  # pylint: disable=using-constant-test
            pass
        elif False:  # pylint: disable=using-constant-test
            pass
        elif False:  # pylint: disable=using-constant-test
            context.push_warning(
                'Mosaic layer “{}” has been removed from the project (Mosaic layers are not supported by QGIS)'.format(
                    source_layer.name), level=Context.CRITICAL)
        elif isinstance(source_layer, (LasDatasetLayer,)):
            pass
        elif isinstance(source_layer, TopologyLayer):
            context.push_warning(
                'Topology layer “{}” has been removed from the project (topology layers are not supported by QGIS)'.format(
                    source_layer.name), level=Context.CRITICAL)
        elif isinstance(source_layer, CadLayer):
            context.push_warning(
                'CAD layer “{}” has been removed from the project (CAD layers are not supported by QGIS)'.format(
                    source_layer.name), level=Context.CRITICAL)
        elif isinstance(source_layer, NetworkLayer):
            context.push_warning(
                'Network layer “{}” has been removed from the project (network layers are not supported by QGIS)'.format(
                    source_layer.name), level=Context.CRITICAL)
        elif False:  # pylint: disable=using-constant-test
            pass
        elif False:  # pylint: disable=using-constant-test
            pass
        elif False:  # pylint: disable=using-constant-test
            context.push_warning(
                'Terrain layer “{}” has been removed from the project (Terrain layers are not supported by QGIS)'.format(
                    source_layer.name), level=Context.CRITICAL)
        elif isinstance(source_layer,
                        (RasterCatalogLayer,)):
            context.push_warning(
                'Raster catalog layer “{}” has been removed from the project (raster catalog layers are not supported by QGIS)'.format(
                    source_layer.name), level=Context.CRITICAL)
        elif False:  # pylint: disable=using-constant-test
            context.push_warning(
                'Globe server layer “{}” has been removed from the project (GlobeServer layers are not supported by QGIS)'.format(
                    source_layer.name), level=Context.CRITICAL)
        elif False:  # pylint: disable=using-constant-test
            context.push_warning(
                '3D Graphics Layer “{}” has been removed from the project (GraphicsLayer3D layers are not supported by QGIS)'.format(
                    source_layer.name), level=Context.CRITICAL)
        elif isinstance(source_layer,
                        (ImageServerLayer,)):
            pass
        elif isinstance(source_layer, WmsLayer):
            pass
        elif isinstance(source_layer, (
                MapServerRESTSubLayer, MapServerSubLayer,)):
            pass
        elif False:  # pylint: disable=using-constant-test
            context.push_warning(
                'Converting annotation layers is not yet supported',
                level=Context.WARNING)
        elif False:  # pylint: disable=using-constant-test
            pass
        else:
            raise NotImplementedException(
                'Converting {} is not yet implemented'.format(
                    source_layer.__class__.__name__))
        context.layer_name = ''
        return [layer for layer in res if layer is not None]

    # pylint: enable=too-many-branches,too-many-statements

    @staticmethod
    def layer_to_QgsDataSourceUri(source, input_file=''):
        """
        Tries to convert a layer source to a QGIS data source URI
        """
        uri = None
        if LayerConverter.is_vector_layer_name(source):
            if isinstance(source, FgdbFeatureClassName):
                uri = '{}|layername={}'.format(source.dataset_name.name,
                                               source.name)
            elif source.__class__.__name__ == 'CoverageFeatureClassName':
                uri = '{}|layername={}'.format(source.datasource_type,
                                               source.name)
            elif isinstance(source, FeatureClassName):
                if source.dataset_name.name[0] == '.':
                    # lyr points to relative file
                    base, _ = os.path.split(input_file)
                    uri = os.path.normpath(
                        '{}/{}/{}.shp'.format(base, source.dataset_name.name,
                                              source.name))
                else:
                    uri = '{}/{}.shp'.format(source.dataset_name.name,
                                             source.name)
        return uri

    @staticmethod
    def object_to_layers_and_tree(obj,
                                  input_file,
                                  context: Context,
                                  definitions=None):  # pylint: disable=unused-argument
        """
        Converts an ESRI object to layers and equivalent layer tree
        """

        layers = []

        def add_layer(layer, group_node):
            nonlocal layers
            results = LayerConverter.layer_to_QgsLayer(layer, input_file,
                                                       context=context,
                                                       fallback_crs=QgsCoordinateReferenceSystem(
                                                           'EPSG:4326'))
            for res in results:
                node = group_node.addLayer(res)
                if not layer.visible:
                    node.setItemVisibilityChecked(False)
                if len(node.children()) > 10:
                    node.setExpanded(False)
                layers.append(res)

        def add_group(group, parent):
            group_node = parent.addGroup(group.name)

            if False:  # pylint: disable=using-constant-test
                pass
            else:
                for c in group.children:
                    if isinstance(c, (GroupLayer, BaseMapLayer)):
                        add_group(c, group_node)
                    else:
                        add_layer(c, group_node)

        root_node = QgsLayerTreeGroup()

        if False:  # pylint: disable=using-constant-test
            pass
        else:
            if LayerConverter.is_layer(obj):
                add_layer(obj, root_node)
            else:
                add_group(obj, root_node)

        return root_node, layers

    @staticmethod
    def object_to_qlr(obj, input_file, output_path, context: Context,
                      use_relative_paths: bool = False,
                      definitions=None) -> Tuple[
        bool, Optional[str]]:
        """
        Converts an ESRI object to QLR
        """

        root_node, _ = LayerConverter.object_to_layers_and_tree(obj,
                                                                input_file,
                                                                context,
                                                                definitions=definitions)

        output_path = QgsFileUtils.ensureFileNameHasExtension(output_path,
                                                              ['qlr'])

        file = QFile(output_path)
        if not file.open(QFile.WriteOnly | QFile.Truncate):
            return False, file.errorString()

        rw_context = QgsReadWriteContext()
        if not use_relative_paths:
            rw_context.setPathResolver(QgsPathResolver())
        else:
            rw_context.setPathResolver(QgsPathResolver(output_path))

        doc = QDomDocument("qgis-layer-definition")
        res, error = QgsLayerDefinition.exportLayerDefinition(doc,
                                                              root_node.children(),
                                                              rw_context)
        if res:
            stream = QTextStream(file)
            doc.save(stream, 2)
            return True, None

        return res, error

    @staticmethod
    def is_layer(obj):
        """
        Returns True if object is a map layer
        """
        return isinstance(obj, (
            CadFeatureLayer, CadLayer, CadAnnotationLayer, FeatureLayer,
            WmsMapLayer,
            RasterLayer, MapServerLayer, InternetTiledLayer, TinLayer,
            MapServerRESTLayer,
            ImageServerLayer, LasDatasetLayer,
            WmtsLayer,
            TopologyLayer,
            NetworkLayer, RasterCatalogLayer,
            RasterBasemapLayer,
            WmsLayer, MapServerRESTSubLayer, MapServerBasicSublayer,
            MapServerSubLayer
        ))

    @staticmethod
    def is_group(obj):
        """
        Returns True if object is a group layer
        """
        return isinstance(obj, (GroupLayer, BaseMapLayer))

    @staticmethod
    def is_vector_layer(obj):
        """
        Returns True if object is a map layer
        """
        return isinstance(obj, (
            CadFeatureLayer, FeatureLayer, CadAnnotationLayer))

    @staticmethod
    def is_vector_layer_name(obj):
        """
        Returns True if object is a vector layer name
        """
        return isinstance(obj, FeatureClassName)

    @staticmethod
    def unique_layer_name_map(obj, definitions=None):  # pylint: disable=unused-argument
        """
        Returns a dict of unique name for layers to layers
        """
        layers = {}

        def add_layer(layer, parent):  # pylint: disable=unused-argument
            nonlocal layers
            original_name = layer.name
            name = original_name
            next_index = 1
            while name in layers:
                next_index += 1
                name = '{}_{}'.format(original_name, next_index)

            layers[name] = layer

        def add_group(group, parent):  # pylint: disable=unused-argument
            if False:  # pylint: disable=using-constant-test
                pass
            else:
                for c in group.children:
                    if isinstance(c, (GroupLayer, BaseMapLayer)):
                        add_group(c, group)
                    else:
                        add_layer(c, group)

        if False:  # pylint: disable=using-constant-test
            pass
        else:
            if LayerConverter.is_layer(obj):
                add_layer(obj, None)
            else:
                add_group(obj, None)

        return layers

    @staticmethod
    def layers_to_qml(obj,  # pylint: disable=too-many-locals
                      input_file, output_file, context: Context, on_error=None,
                      definitions=None):
        """
        Converts layer to QML
        """
        path, name = os.path.split(output_file)
        basename, _ = os.path.splitext(name)

        # CRS are not relevant for QML, so avoid all prompts
        fallback_crs = QgsCoordinateReferenceSystem('EPSG:4326')
        layers = LayerConverter.unique_layer_name_map(obj, definitions)
        for name, layer in layers.items():
            # TODO - handle multiple returns?
            vl = LayerConverter.layer_to_QgsLayer(layer, input_file,
                                                  fallback_crs=fallback_crs,
                                                  context=context)[0]
            if len(layers) == 1:
                url = output_file
            else:
                url = os.path.join(path, '{} {}.qml'.format(basename, name))

            status, res = vl.saveNamedStyle(url)
            if not res and on_error:
                on_error(status)
