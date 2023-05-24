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
Converts parsed symbol properties to QGIS Symbols
"""

#  pylint: disable=too-many-lines

import os
import re
from collections import defaultdict

from qgis.core import (Qgis,
                       QgsCoordinateReferenceSystem,
                       QgsRasterLayer,
                       QgsSingleBandPseudoColorRenderer,
                       QgsCubicRasterResampler,
                       QgsBilinearRasterResampler,
                       QgsDataProvider,
                       QgsRasterResampleFilter,
                       QgsBrightnessContrastFilter,
                       QgsHueSaturationFilter,
                       QgsRasterProjector,
                       QgsMultiBandColorRenderer,
                       QgsPalettedRasterRenderer,
                       QgsRasterShader,
                       QgsColorRampShader,
                       QgsVectorLayer,
                       QgsProviderRegistry,
                       QgsFeatureRequest)

from .color import ColorConverter
from .color_ramp import ColorRampConverter
from .context import Context
from .converter import NotImplementedException
from .crs import CrsConverter
from .utils import ConversionUtils
from ..parser.objects.function_raster_dataset_name import \
    FunctionRasterDatasetName
from ..parser.objects.multi_layer_symbols import MultiLayerFillSymbol
from ..parser.objects.raster_band_name import RasterBandName
from ..parser.objects.raster_basemap_layer import RasterBasemapLayer
from ..parser.objects.raster_classify_color_ramp_renderer import \
    RasterClassifyColorRampRenderer
from ..parser.objects.raster_color_map_renderer import RasterColorMapRenderer
from ..parser.objects.raster_dataset_name import SdeRasterDatasetName, \
    FgdbRasterDatasetName
from ..parser.objects.raster_layer import RasterLayer
from ..parser.objects.raster_renderer import RasterRenderer
from ..parser.objects.raster_rgb_renderer import RasterRGBRenderer
from ..parser.objects.raster_stretch_color_ramp_renderer import \
    RasterStretchColorRampRenderer
from ..parser.objects.raster_unique_value_renderer import \
    RasterUniqueValueRenderer
from ..parser.objects.simple_raster_renderer import SimpleRasterRenderer


class RasterLayerConverter:
    """
    Raster layer conversion methods
    """

    # pylint: disable=too-many-locals
    @staticmethod
    def raster_layer_to_QgsRasterLayer(
            layer: RasterLayer, input_file,
            context: Context,
            fallback_crs=QgsCoordinateReferenceSystem()):
        """
        Converts a raster layer to a QGIS raster layer
        """
        provider = 'gdal'
        base, _ = os.path.split(input_file)
        uri = ''

        def find_neighbour_file(_base: str, _file_name: str) -> str:
            if not os.path.exists(_file_name):
                # look next to .lyr for matching file
                _, _name = os.path.split(_file_name)
                if os.path.exists(os.path.join(_base, _name)):
                    return os.path.join(_base, _name)
            return _file_name

        if False:  # pylint: disable=using-constant-test
            pass
        elif False:  # pylint: disable=using-constant-test
            pass
        else:
            if isinstance(layer.dataset_name, RasterBandName):
                dataset_name = layer.dataset_name.dataset_name
                band = layer.dataset_name.band
            else:
                dataset_name = layer.dataset_name
                band = -1

            if isinstance(dataset_name,
                          (SdeRasterDatasetName, FgdbRasterDatasetName)):
                if ConversionUtils.is_gdal_version_available(3, 7, 0):
                    file_name = ConversionUtils.get_absolute_path(
                        dataset_name.workspace_name.name,
                        base)
                    layer_name = dataset_name.path
                    uri = 'OpenFileGDB:"{}":{}'.format(
                        find_neighbour_file(base, file_name),
                        layer_name
                    )
                else:
                    if isinstance(dataset_name,
                                  FgdbRasterDatasetName) and context.unsupported_object_callback:
                        context.unsupported_object_callback(
                            '{}: Raster layers in Geodatabase files require a newer QGIS version, the database {} will need to be converted to TIFF before it can be used outside of ArcGIS'.format(
                                layer.name, dataset_name.workspace_name.name),
                            level=Context.WARNING)
                    file_name = ConversionUtils.get_absolute_path(
                        dataset_name.workspace_name.name,
                        base)
                    uri = file_name + '|' + dataset_name.file_name
            elif isinstance(dataset_name, FunctionRasterDatasetName):
                file_name = ConversionUtils.get_absolute_path(
                    dataset_name.workspace_name.name,
                    base)
                if file_name[-1] == '/':
                    file_name = file_name[:-1]
                file_name = file_name + '/' + dataset_name.full_name
                uri = find_neighbour_file(base, file_name)
                if context.unsupported_object_callback:
                    context.unsupported_object_callback(
                        'Raster layer “{}” was originally set to use a raster function ({}), these are not supported by QGIS'.format(
                            layer.name,
                            dataset_name.function.__class__.__name__),
                        level=Context.WARNING)
                else:
                    raise NotImplementedException(
                        'Function rasters are not supported by QGIS')
            elif dataset_name.workspace_name.connection_properties:
                if 'DATABASE' in dataset_name.workspace_name.connection_properties.properties:
                    file_name = \
                        dataset_name.workspace_name.connection_properties.properties[
                            'DATABASE'].replace('\\',
                                                '/') + dataset_name.file_name
                else:
                    file_name = \
                        dataset_name.workspace_name.connection_properties.properties[
                            'SERVER'] + dataset_name.file_name
                uri = find_neighbour_file(base, file_name)
            else:
                file_name = ConversionUtils.path_insensitive(
                    '{}/{}'.format(
                        ConversionUtils.get_absolute_path(
                            dataset_name.workspace_name.name, base),
                        dataset_name.file_name))
                uri = find_neighbour_file(base, file_name)

        if Qgis.QGIS_VERSION_INT >= 30900:
            options = QgsRasterLayer.LayerOptions()
            options.skipCrsValidation = True
            rl = QgsRasterLayer(uri, layer.name, provider, options)
        else:
            if provider == 'gdal' and Qgis.QGIS_VERSION_INT < 30900 and not os.path.exists(
                    uri):
                # QGIS raster layers don't like to have invalid data providers when setting symbology
                # so we fake it initially...
                dummy_path = os.path.abspath(os.path.join(
                    os.path.dirname(__file__),
                    '..',
                    'dummy_raster.tif'))
                rl = QgsRasterLayer(dummy_path, layer.name, 'gdal')
            else:
                rl = QgsRasterLayer(uri, layer.name, provider)

        if False:  # pylint: disable=using-constant-test
            crs = QgsCoordinateReferenceSystem()
        else:
            if not False:
                crs = CrsConverter.convert_crs(layer.extent.crs,
                                               context) if layer.extent else QgsCoordinateReferenceSystem()
                if not crs.isValid():
                    crs = fallback_crs
                rl.setCrs(crs)

        metadata = rl.metadata()
        metadata.setAbstract(layer.description)
        rl.setMetadata(metadata)

        if False:  # pylint: disable=using-constant-test
            pass
        else:
            # layer.zoom_max = "don't show when zoomed out beyond"
            zoom_max = layer.zoom_max or 0
            # layer.zoom_min = "don't show when zoomed in beyond"
            zoom_min = layer.zoom_min or 0

            enabled_scale_range = bool(zoom_max or zoom_min)
            if zoom_max and zoom_min and zoom_min > zoom_max:
                # inconsistent scale range -- zoom_max should be bigger number than zoom_min
                tmp = zoom_min
                zoom_min = zoom_max
                zoom_max = tmp

            # qgis minimum scale = don't show when zoomed out beyond, i.e. ArcGIS zoom_max
            rl.setMinimumScale(
                zoom_max if enabled_scale_range else layer.stored_zoom_max)
            # qgis maximum scale = don't show when zoomed in beyond, i.e. ArcGIS zoom_min
            rl.setMaximumScale(
                zoom_min if enabled_scale_range else layer.stored_zoom_min)
            rl.setScaleBasedVisibility(enabled_scale_range)

        brightness_contrast = QgsBrightnessContrastFilter()
        gamma = 1
        if False:  # pylint: disable=using-constant-test
            pass
        else:
            renderer = RasterLayerConverter.convert_raster_renderer(
                layer.renderer, band, rl,
                context)
            if isinstance(layer.renderer, RasterStretchColorRampRenderer):
                gamma = layer.renderer.gamma if layer.renderer.apply_gamma else 1

        if gamma != 1:
            if Qgis.QGIS_VERSION_INT < 31600:
                if context.unsupported_object_callback:
                    context.unsupported_object_callback(
                        'Gamma correction for raster layers requires QGIS 3.16 or later',
                        level=Context.WARNING)
                else:
                    raise NotImplementedException(
                        'Setting the gamma for raster layers requires QGIS 3.16 or later')
            else:
                brightness_contrast.setGamma(gamma)

        if renderer:
            renderer.setOpacity(1.0 - (layer.transparency or 0) / 100)
            rl.setRenderer(renderer)

        # we have to manually setup a default raster pipeline, because this isn't done for broken layer paths

        rl.pipe().set(brightness_contrast)
        rl.pipe().set(QgsHueSaturationFilter())
        rl.pipe().set(QgsRasterResampleFilter())
        if False:  # pylint: disable=using-constant-test
            pass
        else:
            if layer.renderer.resampling_type in (
                    RasterRenderer.RESAMPLING_BILINEAR,
                    RasterRenderer.RESAMPLING_BILINEAR_PLUS):
                rl.resampleFilter().setZoomedInResampler(
                    QgsBilinearRasterResampler())
                rl.resampleFilter().setZoomedOutResampler(
                    QgsBilinearRasterResampler())
            elif layer.renderer.resampling_type == RasterRenderer.RESAMPLING_CUBIC:
                rl.resampleFilter().setZoomedInResampler(
                    QgsCubicRasterResampler())
                rl.resampleFilter().setZoomedOutResampler(
                    QgsBilinearRasterResampler())  # can't use cubic for zoomed out
        rl.pipe().set(QgsRasterProjector())

        if Qgis.QGIS_VERSION_INT >= 306000 and Qgis.QGIS_VERSION_INT < 30900:
            rl.setDataSource(uri, layer.name, 'gdal',
                             QgsDataProvider.ProviderOptions())

        if False:  # pylint: disable=using-constant-test
            pass

        return rl

    # pylint: enable=too-many-locals

    @staticmethod
    def raster_basemap_layer_to_QgsRasterLayer(
            source_layer: RasterBasemapLayer, input_file,
            context: Context,
            fallback_crs=QgsCoordinateReferenceSystem()):
        if source_layer.raster_layer:
            return [RasterLayerConverter.raster_layer_to_QgsRasterLayer(
                source_layer.raster_layer,
                input_file, context,
                fallback_crs)]
        return []

    @staticmethod
    def convert_raster_renderer(renderer, band, layer, context):
        res = None
        if isinstance(renderer, (RasterStretchColorRampRenderer,)):
            if band >= 0:
                renderer_band = band
            elif False:  # pylint: disable=using-constant-test
                pass
            else:
                renderer_band = renderer.band
            res = QgsSingleBandPseudoColorRenderer(layer.dataProvider(),
                                                   renderer_band)
            color_ramp = ColorRampConverter.ColorRamp_to_QgsColorRamp(
                renderer.color_ramp)
            if renderer.invert_stretch:
                color_ramp.invert()

            if False:  # pylint: disable=using-constant-test
                pass
            else:
                min_value = renderer.min_value
                max_value = renderer.max_value
            res.setClassificationMin(min_value or 0)
            res.setClassificationMax(max_value or 0)

            if min_value == max_value:
                ramp_shader = QgsColorRampShader(min_value, max_value,
                                                 color_ramp,
                                                 QgsColorRampShader.Interpolated,
                                                 QgsColorRampShader.Continuous)
                shader = QgsRasterShader()
                shader.setRasterShaderFunction(ramp_shader)
                res.setShader(shader)
            else:
                res.createShader(color_ramp)
        elif isinstance(renderer, RasterRGBRenderer):
            res = QgsMultiBandColorRenderer(layer.dataProvider(),
                                            renderer.red_band if renderer.red_checked else -1,
                                            renderer.green_band if renderer.green_checked else -1,
                                            renderer.blue_band if renderer.blue_checked else -1)
        elif False:  # pylint: disable=using-constant-test
            pass
        elif isinstance(renderer, (RasterUniqueValueRenderer,)):
            uri = QgsProviderRegistry.instance().decodeUri(
                layer.providerType(), layer.source())
            rat_lookup_table = defaultdict(list)
            if 'path' in uri:
                if os.path.exists(uri['path'] + '.vat.dbf'):
                    rat = QgsVectorLayer(uri['path'] + '.vat.dbf', 'rat',
                                         'ogr')
                    if rat.isValid() and renderer.legend_groups:
                        legend_group = renderer.legend_groups[0].heading
                        field_idx = rat.fields().lookupField(legend_group)
                        value_idx = rat.fields().lookupField('Value')
                        if field_idx >= 0 and value_idx >= 0:
                            request = QgsFeatureRequest().setSubsetOfAttributes(
                                [field_idx, value_idx])
                            for f in rat.getFeatures(request):
                                value = f[value_idx]
                                rat_lookup_table[f[field_idx]].append(value)

            classes = []
            legend_group = 0
            legend_class = 0

            if isinstance(renderer, RasterUniqueValueRenderer):
                for i, c in enumerate(renderer.values):
                    if legend_class >= len(
                            renderer.legend_groups[legend_group].classes):
                        legend_class = 0
                        legend_group += 1

                    legend = renderer.legend_groups[legend_group].classes[
                        legend_class]
                    legend_class += 1

                    for v in c:
                        if isinstance(legend.symbol, MultiLayerFillSymbol):
                            color = ColorConverter.color_to_qcolor(
                                legend.symbol.layers[0].color)
                        else:
                            color = ColorConverter.color_to_qcolor(
                                legend.symbol.color)
                        if isinstance(v, str):
                            # raster attribute table!
                            val_match = re.match(r'(\d+)_.*?', v)
                            if val_match:
                                v = int(val_match.group(1))
                                cl = QgsPalettedRasterRenderer.Class(v, color,
                                                                     legend.label)
                                classes.append(cl)
                            elif v in rat_lookup_table:
                                for pixel_value in rat_lookup_table[v]:
                                    cl = QgsPalettedRasterRenderer.Class(
                                        pixel_value, color,
                                        legend.label)
                                    classes.append(cl)
                            elif renderer.unique_values and len(
                                    renderer.unique_values.values) > i:
                                v = renderer.unique_values.values[i][0]
                                cl = QgsPalettedRasterRenderer.Class(v, color,
                                                                     legend.label)
                                classes.append(cl)
                            elif len(renderer.backup_value_count) > i:
                                v = renderer.backup_value_count[i][0]
                                cl = QgsPalettedRasterRenderer.Class(v, color,
                                                                     legend.label)
                                classes.append(cl)
                        else:
                            cl = QgsPalettedRasterRenderer.Class(v, color,
                                                                 legend.label)
                            classes.append(cl)
            else:
                pass

            renderer_band = band if band >= 0 else 1
            res = QgsPalettedRasterRenderer(layer.dataProvider(),
                                            renderer_band,
                                            classes)
            if renderer.ramp:
                color_ramp = ColorRampConverter.ColorRamp_to_QgsColorRamp(
                    renderer.ramp)
                # if layer.renderer.invert_stretch:
                #    color_ramp.invert()
                res.setSourceColorRamp(color_ramp)
        elif isinstance(renderer, (RasterColorMapRenderer,)):
            classes = []
            for i, v in enumerate(renderer.values):
                if False:  # pylint: disable=using-constant-test
                    pass
                else:
                    if len(renderer.groups[0].classes) <= i:
                        # sometimes more values are present than classes, for an unknown reason. Possibly corrupt document??
                        break

                    legend = renderer.groups[0].classes[i].label
                    color = ColorConverter.color_to_qcolor(
                        renderer.groups[0].classes[i].symbol.color)
                cl = QgsPalettedRasterRenderer.Class(v, color, legend)
                classes.append(cl)

            renderer_band = band if band >= 0 else 1
            res = QgsPalettedRasterRenderer(layer.dataProvider(),
                                            renderer_band,
                                            classes)
        elif isinstance(renderer, (RasterClassifyColorRampRenderer,)):
            if band >= 0:
                renderer_band = band
            else:
                renderer_band = 1

            res = QgsSingleBandPseudoColorRenderer(layer.dataProvider(),
                                                   renderer_band)
            if isinstance(renderer, RasterClassifyColorRampRenderer):
                min = renderer.breaks[0]
                max = renderer.breaks[-1]
            else:
                min = renderer.minimum_break or 0
                max = renderer.class_breaks[-1].upper_bound

            res.setClassificationMin(min)
            res.setClassificationMax(max)

            if renderer.color_ramp:
                color_ramp = ColorRampConverter.ColorRamp_to_QgsColorRamp(
                    renderer.color_ramp)
            else:
                color_ramp = None

            shader = QgsRasterShader(min, max)
            shader_function = QgsColorRampShader(min, max, color_ramp,
                                                 type=QgsColorRampShader.Discrete)

            items = []
            if isinstance(renderer, RasterClassifyColorRampRenderer):
                for i, b in enumerate(renderer.breaks[1:]):

                    legend_group = i
                    if not renderer.sort_classes_ascending:
                        legend_group = len(
                            renderer.legend_group.classes) - i - 1

                    item = QgsColorRampShader.ColorRampItem(b,
                                                            ColorConverter.color_to_qcolor(
                                                                renderer.legend_group.classes[
                                                                    legend_group].symbol.color),
                                                            renderer.legend_group.classes[
                                                                legend_group].label)
                    items.append(item)
            else:
                pass
            shader_function.setColorRampItemList(items)
            shader.setRasterShaderFunction(shader_function)
            res.setShader(shader)
        elif isinstance(renderer, SimpleRasterRenderer):
            # do nothing, use default renderer...
            pass
        else:
            raise NotImplementedException(
                'Raster {} not yet implemented'.format(
                    renderer.__class__.__name__))

        if False:  # pylint: disable=using-constant-test
            pass
        elif True:  # pylint: disable=using-constant-test
            if renderer and renderer.alpha_band is not None and renderer.alpha_checked:
                res.setAlphaBand(renderer.alpha_band)

        if renderer and (False and renderer.nodata_color) or (
                True and not renderer.nodata_color.is_null):
            # This isn't correct - I don't see anyway to add manual no data pixels to rasters in arc
            # transparency = QgsRasterTransparency()
            # no_data_color = ColorConverter.color_to_qcolor(layer.renderer.nodata_color)
            # transparency.initializeTransparentPixelList(no_data_color.red(), no_data_color.green(), no_data_color.blue())
            # renderer.setRasterTransparency(transparency)
            if Qgis.QGIS_VERSION_INT < 31100:
                if context.unsupported_object_callback:
                    context.unsupported_object_callback(
                        'Setting the color for nodata pixels requires QGIS 3.12 or later',
                        level=Context.WARNING)
                else:
                    raise NotImplementedException(
                        'Setting the color for nodata pixels requires QGIS 3.12 or later')
            else:
                res.setNodataColor(
                    ColorConverter.color_to_qcolor(renderer.nodata_color))

        return res
