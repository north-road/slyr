"""
Raster layer conversion
"""

# /***************************************************************************
#  *                                                                         *
#  *   This program is free software; you can redistribute it and/or modify  *
#  *   it under the terms of the GNU General Public License as published by  *
#  *   the Free Software Foundation; either version 2 of the License, or     *
#  *   (at your option) any later version.                                   *
#  *                                                                         *
#  ***************************************************************************/

#  pylint: disable=too-many-lines

import os
import re
import urllib.parse
from collections import defaultdict

from qgis.PyQt.QtCore import QUrl, QUrlQuery
from qgis.core import (
    Qgis,
    QgsRaster,
    QgsCoordinateReferenceSystem,
    QgsRasterLayer,
    QgsSingleBandPseudoColorRenderer,
    QgsCubicRasterResampler,
    QgsBilinearRasterResampler,
    QgsRasterResampleFilter,
    QgsBrightnessContrastFilter,
    QgsHueSaturationFilter,
    QgsRasterProjector,
    QgsMultiBandColorRenderer,
    QgsPalettedRasterRenderer,
    QgsRasterTransparency,
    QgsRasterShader,
    QgsColorRampShader,
    QgsVectorLayer,
    QgsProviderRegistry,
    QgsFeatureRequest,
)

from .color import ColorConverter
from .color_ramp import ColorRampConverter
from .context import Context
from .converter import NotImplementedException
from .crs import CrsConverter
from .dataset_name import DatasetNameConverter
from .symbols import SymbolConverter
from .utils import ConversionUtils

from ..parser.objects.function_raster_dataset_name import FunctionRasterDatasetName
from ..parser.objects.image_server_layer import ImageServerLayer
from ..parser.objects.internet_tiled_layer import InternetTiledLayer
from ..parser.objects.map_server_layer import MapServerLayer, MapServerSubLayer
from ..parser.objects.map_server_rest_layer import MapServerRESTLayer
from ..parser.objects.multi_layer_symbols import MultiLayerFillSymbol
from ..parser.objects.raster_band_name import RasterBandName
from ..parser.objects.raster_basemap_layer import RasterBasemapLayer
from ..parser.objects.raster_classify_color_ramp_renderer import (
    RasterClassifyColorRampRenderer,
)
from ..parser.objects.raster_color_map_renderer import RasterColorMapRenderer
from ..parser.objects.raster_dataset_name import (
    SdeRasterDatasetName,
    FgdbRasterDatasetName,
)
from ..parser.objects.raster_layer import RasterLayer
from ..parser.objects.raster_renderer import RasterRenderer
from ..parser.objects.raster_rgb_renderer import RasterRGBRenderer
from ..parser.objects.raster_stretch_color_ramp_renderer import (
    RasterStretchColorRampRenderer,
)
from ..parser.objects.raster_unique_value_renderer import RasterUniqueValueRenderer
from ..parser.objects.simple_raster_renderer import SimpleRasterRenderer
from ..parser.objects.wms_layer import WmsMapLayer, WmsGroupLayer
from ..parser.objects.wmts_layer import WmtsLayer
from ..parser.objects.workspace_name import WorkspaceName


class RasterLayerConverter:
    """
    Raster layer conversion methods
    """

    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    @staticmethod
    def raster_layer_to_QgsRasterLayer(
        layer: RasterLayer,
        input_file: str,
        context: Context,
        fallback_crs=QgsCoordinateReferenceSystem(),
    ):
        """
        Converts a raster layer to a QGIS raster layer
        """

        provider = "gdal"
        base, _ = os.path.split(input_file)
        uri = ""

        is_raster_gdb = False
        if isinstance(layer.dataset_name, RasterBandName):
            dataset_name = layer.dataset_name.dataset_name
            band = layer.dataset_name.band
        else:
            dataset_name = layer.dataset_name
            band = -1

        if isinstance(dataset_name, (SdeRasterDatasetName, FgdbRasterDatasetName)):
            is_raster_gdb = True
            if ConversionUtils.is_gdal_version_available(3, 7, 0):
                file_name = ConversionUtils.get_absolute_path(
                    dataset_name.workspace_name.name, base
                )
                layer_name = dataset_name.path
                uri = 'OpenFileGDB:"{}":{}'.format(
                    context.resolve_filename(input_file, file_name), layer_name
                )
            else:
                context.push_warning(
                    "{}: Raster layers in Geodatabase files require a newer QGIS version, the database {} will need to be converted to TIFF before it can be used outside of ArcGIS".format(
                        layer.name, dataset_name.workspace_name.name
                    ),
                    level=Context.WARNING,
                )
                file_name = ConversionUtils.get_absolute_path(
                    dataset_name.workspace_name.name, base
                )
                uri = file_name + "|" + dataset_name.file_name
        elif isinstance(dataset_name, FunctionRasterDatasetName):
            file_name = ConversionUtils.get_absolute_path(
                dataset_name.workspace_name.name, base
            )
            if file_name[-1] == "/":
                file_name = file_name[:-1]
            file_name = file_name + "/" + dataset_name.full_name
            uri = context.resolve_filename(input_file, file_name)
            context.push_warning(
                "Raster layer “{}” was originally set to use a raster function ({}), these are not supported by QGIS".format(
                    layer.name, dataset_name.function.__class__.__name__
                ),
                level=Context.WARNING,
            )
        elif dataset_name.workspace_name.connection_properties:
            if (
                "DATABASE"
                in dataset_name.workspace_name.connection_properties.properties
            ):
                file_name = (
                    dataset_name.workspace_name.connection_properties.properties[
                        "DATABASE"
                    ].replace("\\", "/")
                    + dataset_name.file_name
                )
            else:
                file_name = (
                    dataset_name.workspace_name.connection_properties.properties[
                        "SERVER"
                    ]
                    + dataset_name.file_name
                )
            uri = context.resolve_filename(input_file, file_name)
        else:
            file_name = ConversionUtils.path_insensitive(
                "{}/{}".format(
                    ConversionUtils.get_absolute_path(
                        dataset_name.workspace_name.name, base
                    ),
                    dataset_name.file_name,
                )
            )
            uri = context.resolve_filename(input_file, file_name)

        options = QgsRasterLayer.LayerOptions()
        options.skipCrsValidation = True
        rl = QgsRasterLayer(uri, layer.name, provider, options)

        if True:
            crs = (
                CrsConverter.convert_crs(layer.extent.crs, context)
                if layer.extent
                else QgsCoordinateReferenceSystem()
            )
            if not crs.isValid():
                crs = fallback_crs
            rl.setCrs(crs)

        metadata = rl.metadata()
        metadata.setAbstract(layer.description)
        rl.setMetadata(metadata)

        # layer.zoom_max = "don't show when zoomed out beyond"
        zoom_max = layer.zoom_max or 0
        # layer.zoom_min = "don't show when zoomed in beyond"
        zoom_min = layer.zoom_min or 0

        enabled_scale_range = bool(zoom_max or zoom_min)
        if zoom_max and zoom_min and zoom_min > zoom_max:
            # inconsistent scale range -- zoom_max should be bigger number than zoom_min
            zoom_min, zoom_max = zoom_max, zoom_min

        # qgis minimum scale = don't show when zoomed out beyond, i.e. ArcGIS zoom_max
        rl.setMinimumScale(zoom_max if enabled_scale_range else layer.stored_zoom_max)
        # qgis maximum scale = don't show when zoomed in beyond, i.e. ArcGIS zoom_min
        rl.setMaximumScale(zoom_min if enabled_scale_range else layer.stored_zoom_min)
        rl.setScaleBasedVisibility(enabled_scale_range)

        def apply_colorizer(source):
            brightness_contrast = QgsBrightnessContrastFilter()
            gamma = 1
            invert = False
            renderer = RasterLayerConverter.convert_raster_renderer(
                source, band, rl, context
            )
            if isinstance(source, RasterStretchColorRampRenderer):
                gamma = source.gamma if source.apply_gamma else 1
            elif isinstance(source, RasterRGBRenderer):
                if source.apply_gamma:
                    if (source.red_gamma != source.green_gamma) or (
                        source.red_gamma != source.blue_gamma
                    ):
                        context.push_warning(
                            "Different per band gamma stretch values are not permitted in QGIS",
                        )
                    gamma = (
                        source.red_gamma + source.green_gamma + source.blue_gamma
                    ) / 3

            if gamma != 1:
                brightness_contrast.setGamma(gamma)

            if renderer:
                renderer.setOpacity(1.0 - (layer.transparency or 0) / 100)
                rl.setRenderer(renderer)

                if is_raster_gdb and renderer.alphaBand() == -1:
                    if rl.isValid():
                        for _band in range(1, rl.dataProvider().bandCount() + 1):
                            if (
                                rl.dataProvider().colorInterpretation(_band)
                                == QgsRaster.ColorInterpretation.AlphaBand
                            ):
                                renderer.setAlphaBand(_band)
                                break
                    else:
                        context.push_warning(
                            "Raster GeoDatabase is not available at time of conversion. The transparency band for this layer may need to be manually set after repairing the layer source."
                        )

            # we have to manually setup a default raster pipeline, because this isn't done for broken layer paths

            rl.pipe().set(brightness_contrast)
            hue_filter = QgsHueSaturationFilter()
            if invert:
                hue_filter.setInvertColors(True)
            rl.pipe().set(hue_filter)
            rl.pipe().set(QgsRasterResampleFilter())
            if source.resampling_type in (
                RasterRenderer.RESAMPLING_BILINEAR,
                RasterRenderer.RESAMPLING_BILINEAR_PLUS,
            ):
                rl.resampleFilter().setZoomedInResampler(QgsBilinearRasterResampler())
                rl.resampleFilter().setZoomedOutResampler(QgsBilinearRasterResampler())
            elif source.resampling_type == RasterRenderer.RESAMPLING_CUBIC:
                rl.resampleFilter().setZoomedInResampler(QgsCubicRasterResampler())
                rl.resampleFilter().setZoomedOutResampler(
                    QgsBilinearRasterResampler()
                )  # can't use cubic for zoomed out
            rl.pipe().set(QgsRasterProjector())

        apply_colorizer(layer.renderer)

        return rl

    # pylint: enable=too-many-locals,too-many-branches,too-many-statements

    @staticmethod
    def raster_basemap_layer_to_QgsRasterLayer(
        source_layer: RasterBasemapLayer,
        input_file: str,
        context: Context,
        fallback_crs=QgsCoordinateReferenceSystem(),
    ):
        """
        Converts a raster basemap layer to a raster layer
        """
        if source_layer.raster_layer:
            return [
                RasterLayerConverter.raster_layer_to_QgsRasterLayer(
                    source_layer.raster_layer, input_file, context, fallback_crs
                )
            ]
        return []

    @staticmethod
    def imageserver_layer_to_QgsRasterLayer(
        source_layer: ImageServerLayer,
        input_file: str,
        context: Context,
        fallback_crs=QgsCoordinateReferenceSystem(),
    ):
        if isinstance(source_layer.dataset_name, WorkspaceName):
            base, _ = os.path.split(input_file)

            file_name = ConversionUtils.get_absolute_path(
                source_layer.dataset_name.name, base
            )

            options = QgsRasterLayer.LayerOptions()
            options.skipCrsValidation = True
            res = QgsRasterLayer(file_name, source_layer.name, "gdal", options)

            if source_layer.renderer:
                renderer = RasterLayerConverter.convert_raster_renderer(
                    source_layer.renderer, -1, res, context
                )
                if renderer:
                    renderer.setOpacity(1.0 - source_layer.transparency / 100)
                    res.setRenderer(renderer)

        else:
            url = source_layer.dataset_name.url

            insensitive_hippo = re.compile(re.escape("/services/"), re.IGNORECASE)
            url = insensitive_hippo.sub("/rest/services/", url)

            if context.upgrade_http_to_https:
                url = url.replace("http://", "https://")

            uri = "crs='EPSG:3857' format='PNG32' layer='' url='{}'".format(url)
            if context.ignore_online_sources:
                uri = ""

            uri = DatasetNameConverter.add_stored_arcgis_rest_connection_params_to_uri(
                uri, context
            )

            name = source_layer.name or source_layer.dataset_name.name
            res = QgsRasterLayer(uri, name, "arcgismapserver")

        # layer.zoom_max = "don't show when zoomed out beyond"
        zoom_max = source_layer.zoom_max
        # layer.zoom_min = "don't show when zoomed in beyond"
        zoom_min = source_layer.zoom_min

        enabled_scale_range = zoom_max or zoom_min
        if zoom_max and zoom_min and zoom_min > zoom_max:
            # inconsistent scale range -- zoom_max should be bigger number than zoom_min
            zoom_min, zoom_max = zoom_max, zoom_min

        if enabled_scale_range:
            # qgis minimum scale = don't show when zoomed out beyond, i.e. ArcGIS zoom_max
            res.setMinimumScale(zoom_max)
            # qgis maximum scale = don't show when zoomed in beyond, i.e. ArcGIS zoom_min
            res.setMaximumScale(zoom_min)
            res.setScaleBasedVisibility(True)

        return [res]

    # pylint: disable=too-many-locals, too-many-branches, too-many-statements, too-many-nested-blocks
    @staticmethod
    def convert_raster_renderer(renderer, band, layer, context):
        """
        Converts a raster layer renderer to QGIS renderer
        """

        res = None
        if isinstance(renderer, RasterStretchColorRampRenderer):
            if band >= 0:
                renderer_band = band
            else:
                renderer_band = renderer.band
            res = QgsSingleBandPseudoColorRenderer(layer.dataProvider(), renderer_band)
            color_ramp = ColorRampConverter.ColorRamp_to_QgsColorRamp(
                renderer.color_ramp
            )
            if color_ramp and renderer.invert_stretch:
                color_ramp.invert()

            min_value = renderer.min_value or 0
            max_value = renderer.max_value or 0
            res.setClassificationMin(min_value)
            res.setClassificationMax(max_value)

            if min_value == max_value:
                ramp_shader = QgsColorRampShader(
                    min_value,
                    max_value,
                    color_ramp,
                    QgsColorRampShader.Type.Interpolated,
                    QgsColorRampShader.ClassificationMode.Continuous,
                )
                shader = QgsRasterShader()
                shader.setRasterShaderFunction(ramp_shader)
                res.setShader(shader)
            else:
                res.createShader(color_ramp)
        elif isinstance(renderer, RasterRGBRenderer):
            res = QgsMultiBandColorRenderer(
                layer.dataProvider(),
                renderer.red_band if renderer.red_checked else -1,
                renderer.green_band if renderer.green_checked else -1,
                renderer.blue_band if renderer.blue_checked else -1,
            )
        elif isinstance(renderer, RasterUniqueValueRenderer):
            uri = QgsProviderRegistry.instance().decodeUri(
                layer.providerType(), layer.source()
            )
            rat_lookup_table = defaultdict(list)
            if "path" in uri:
                if os.path.exists(uri["path"] + ".vat.dbf"):
                    rat = QgsVectorLayer(uri["path"] + ".vat.dbf", "rat", "ogr")
                    if rat.isValid():
                        if (
                            isinstance(renderer, RasterUniqueValueRenderer)
                            and renderer.legend_groups
                        ):
                            legend_group = renderer.legend_groups[0].heading
                            field_idx = rat.fields().lookupField(legend_group)
                            value_idx = rat.fields().lookupField("Value")
                            if field_idx >= 0 and value_idx >= 0:
                                request = QgsFeatureRequest().setSubsetOfAttributes(
                                    [field_idx, value_idx]
                                )
                                for f in rat.getFeatures(request):
                                    value = f[value_idx]
                                    rat_lookup_table[f[field_idx]].append(value)

            classes = []
            legend_group = 0
            legend_class = 0

            if isinstance(renderer, RasterUniqueValueRenderer):
                for i, c in enumerate(renderer.values):
                    if legend_class >= len(
                        renderer.legend_groups[legend_group].classes
                    ):
                        legend_class = 0
                        legend_group += 1

                    legend = renderer.legend_groups[legend_group].classes[legend_class]
                    legend_class += 1

                    for v in c:
                        if isinstance(legend.symbol, MultiLayerFillSymbol):
                            color = ColorConverter.color_to_qcolor(
                                legend.symbol.layers[0].color
                            )
                        else:
                            color = ColorConverter.color_to_qcolor(legend.symbol.color)
                        if isinstance(v, str):
                            # raster attribute table!
                            val_match = re.match(r"(\d+)_.*?", v)
                            if val_match:
                                v = int(val_match.group(1))
                                cl = QgsPalettedRasterRenderer.Class(
                                    v, color, legend.label
                                )
                                classes.append(cl)
                            elif v in rat_lookup_table:
                                for pixel_value in rat_lookup_table[v]:
                                    cl = QgsPalettedRasterRenderer.Class(
                                        pixel_value, color, legend.label
                                    )
                                    classes.append(cl)
                            elif (
                                renderer.unique_values
                                and len(renderer.unique_values.values) > i
                            ):
                                v = renderer.unique_values.values[i][0]
                                cl = QgsPalettedRasterRenderer.Class(
                                    v, color, legend.label
                                )
                                classes.append(cl)
                            elif len(renderer.backup_value_count) > i:
                                v = renderer.backup_value_count[i][0]
                                cl = QgsPalettedRasterRenderer.Class(
                                    v, color, legend.label
                                )
                                classes.append(cl)
                        else:
                            cl = QgsPalettedRasterRenderer.Class(v, color, legend.label)
                            classes.append(cl)
            else:
                for legend_group in renderer.groups:
                    for c in legend_group.classes:
                        color = ColorConverter.color_to_qcolor(c.color)

                        for v in c.values:
                            if isinstance(v, str):
                                try:
                                    val = int(v)
                                    cl = QgsPalettedRasterRenderer.Class(
                                        val, color, c.label
                                    )
                                    classes.append(cl)
                                except ValueError:
                                    # raster attribute table!
                                    val_match = re.match(r"(\d+)_.*?", v)
                                    if val_match:
                                        v = int(val_match.group(1))
                                        cl = QgsPalettedRasterRenderer.Class(
                                            v, color, c.label
                                        )
                                        classes.append(cl)
                                    elif v in rat_lookup_table:
                                        for pixel_value in rat_lookup_table[v]:
                                            cl = QgsPalettedRasterRenderer.Class(
                                                pixel_value, color, c.label
                                            )
                                            classes.append(cl)
                            else:
                                cl = QgsPalettedRasterRenderer.Class(v, color, c.label)
                                classes.append(cl)

            renderer_band = band if band >= 0 else 1
            res = QgsPalettedRasterRenderer(
                layer.dataProvider(), renderer_band, classes
            )
            if renderer.ramp:
                color_ramp = ColorRampConverter.ColorRamp_to_QgsColorRamp(renderer.ramp)
                # if layer.renderer.invert_stretch:
                #    color_ramp.invert()
                res.setSourceColorRamp(color_ramp)
        elif isinstance(renderer, RasterColorMapRenderer):
            classes = []
            for i, v in enumerate(renderer.values):
                if len(renderer.groups[0].classes) <= i:
                    # sometimes more values are present than classes, for an unknown reason. Possibly corrupt document??
                    break

                legend = renderer.groups[0].classes[i].label
                color = ColorConverter.color_to_qcolor(
                    renderer.groups[0].classes[i].symbol.color
                )
                cl = QgsPalettedRasterRenderer.Class(v, color, legend)
                classes.append(cl)

            renderer_band = band if band >= 0 else 1
            res = QgsPalettedRasterRenderer(
                layer.dataProvider(), renderer_band, classes
            )
        elif isinstance(renderer, RasterClassifyColorRampRenderer):
            if band >= 0:
                renderer_band = band
            else:
                renderer_band = 1

            res = QgsSingleBandPseudoColorRenderer(layer.dataProvider(), renderer_band)
            raster_min = renderer.breaks[0]
            raster_max = renderer.breaks[-1]

            res.setClassificationMin(raster_min)
            res.setClassificationMax(raster_max)

            if renderer.color_ramp:
                color_ramp = ColorRampConverter.ColorRamp_to_QgsColorRamp(
                    renderer.color_ramp
                )
            else:
                color_ramp = None

            shader = QgsRasterShader(raster_min, raster_max)
            shader_function = QgsColorRampShader(
                raster_min,
                raster_max,
                color_ramp,
                type=QgsColorRampShader.Type.Discrete,
            )

            items = []
            for i, b in enumerate(renderer.breaks[1:]):
                legend_group = i
                if not renderer.sort_classes_ascending:
                    legend_group = len(renderer.legend_group.classes) - i - 1

                symbol = renderer.legend_group.classes[legend_group].symbol
                symbol_color = SymbolConverter.symbol_to_color(symbol, context)
                item = QgsColorRampShader.ColorRampItem(
                    b,
                    symbol_color,
                    renderer.legend_group.classes[legend_group].label,
                )
                items.append(item)
            shader_function.setColorRampItemList(items)
            shader.setRasterShaderFunction(shader_function)
            res.setShader(shader)
        elif isinstance(renderer, SimpleRasterRenderer):
            # do nothing, use default renderer...
            pass
        else:
            raise NotImplementedException(
                "Raster {} not yet implemented".format(renderer.__class__.__name__)
            )

        if renderer and renderer.alpha_band is not None and renderer.alpha_checked:
            res.setAlphaBand(renderer.alpha_band)

        if renderer and not renderer.nodata_color.is_null:
            res.setNodataColor(ColorConverter.color_to_qcolor(renderer.nodata_color))

        if renderer and isinstance(renderer, RasterRGBRenderer):
            if renderer.display_background_value:
                background_color = ColorConverter.color_to_qcolor(
                    renderer.background_color
                )
                if background_color.alpha() == 0:
                    transparency = QgsRasterTransparency()
                    transparency.initializeTransparentPixelList(
                        renderer.background_value_red or 0,
                        renderer.background_value_green or 0,
                        renderer.background_value_blue or 0,
                    )
                    res.setRasterTransparency(transparency)
        elif renderer and isinstance(renderer, RasterStretchColorRampRenderer):
            if renderer.display_background_value:
                background_color = ColorConverter.color_to_qcolor(
                    renderer.background_color
                )
                if background_color.alpha() == 0:
                    transparency = QgsRasterTransparency()
                    transparency.initializeTransparentPixelList(
                        renderer.background_value
                    )
                    res.setRasterTransparency(transparency)
        return res

    # pylint: enable=too-many-locals, too-many-branches, too-many-statements, too-many-nested-blocks

    @staticmethod
    def mapserver_sublayer_to_QgsRasterLayers(
        url,
        source_layer: MapServerSubLayer,
        input_file: str,
        context: Context,
        fallback_crs=QgsCoordinateReferenceSystem(),
    ):
        sub_layer_id = source_layer.index

        if context.upgrade_http_to_https:
            url = url.replace("http://", "https://")

        uri = "crs='EPSG:3857' format='PNG32' layer='' url='{}' layer='{}'".format(
            url, sub_layer_id
        )
        if context.ignore_online_sources:
            uri = ""
        uri = DatasetNameConverter.add_stored_arcgis_rest_connection_params_to_uri(
            uri, context
        )

        res = [QgsRasterLayer(uri, source_layer.name, "arcgismapserver")]
        if isinstance(source_layer, MapServerSubLayer):
            for c in source_layer.children:
                res.extend(
                    RasterLayerConverter.mapserver_sublayer_to_QgsRasterLayers(
                        url, c, input_file, context, fallback_crs
                    )
                )

        return res

    @staticmethod
    def mapserver_rest_layer_to_QgsRasterLayer(
        source_layer: MapServerRESTLayer,
        input_file: str,
        context: Context,
        fallback_crs=QgsCoordinateReferenceSystem(),
    ):
        url = source_layer.url

        if context.upgrade_http_to_https:
            url = url.replace("http://", "https://")

        uri = "crs='EPSG:3857' format='PNG32' layer='' url='{}'".format(url)
        if context.ignore_online_sources:
            uri = ""
        uri = DatasetNameConverter.add_stored_arcgis_rest_connection_params_to_uri(
            uri, context
        )
        res = QgsRasterLayer(uri, source_layer.name, "arcgismapserver")
        return [res]

    @staticmethod
    def mapserver_layer_to_QgsRasterLayer(
        source_layer: MapServerLayer,
        input_file: str,
        context: Context,
        fallback_crs=QgsCoordinateReferenceSystem(),
    ):
        if isinstance(source_layer, MapServerLayer):
            url = source_layer.dataset_name.url
        else:
            url = source_layer.service_connection.url

        if isinstance(source_layer, MapServerLayer):
            insensitive_service_match = re.compile(
                re.escape("/services/"), re.IGNORECASE
            )
            url = insensitive_service_match.sub("/rest/services/", url)

        if context.upgrade_http_to_https:
            url = url.replace("http://", "https://")

        uri = "crs='EPSG:3857' format='PNG32' layer='' url='{}'".format(url)

        if context.ignore_online_sources:
            uri = ""
        uri = DatasetNameConverter.add_stored_arcgis_rest_connection_params_to_uri(
            uri, context
        )
        res = QgsRasterLayer(uri, source_layer.name, "arcgismapserver")

        # layer.zoom_max = "don't show when zoomed out beyond"
        zoom_max = source_layer.zoom_min or 0
        # layer.zoom_min = "don't show when zoomed in beyond"
        zoom_min = source_layer.zoom_max or 0

        enabled_scale_range = zoom_max or zoom_min
        if zoom_max and zoom_min and zoom_min < zoom_max:
            # inconsistent scale range -- zoom_min should be bigger number than zoom_max
            zoom_min, zoom_max = zoom_max, zoom_min

        if enabled_scale_range:
            # qgis minimum scale = don't show when zoomed out beyond, i.e. ArcGIS zoom_max
            res.setMinimumScale(zoom_max)
            # qgis maximum scale = don't show when zoomed in beyond, i.e. ArcGIS zoom_min
            res.setMaximumScale(zoom_min)
            res.setScaleBasedVisibility(True)

        res = []

        for c in source_layer.children:
            res.extend(
                RasterLayerConverter.mapserver_sublayer_to_QgsRasterLayers(
                    url, c, input_file, context, fallback_crs
                )
            )

        for r in res:
            if r.renderer():
                r.renderer().setOpacity(1.0 - (source_layer.transparency or 0) / 100)
            metadata = r.metadata()
            metadata.setAbstract(source_layer.description)
            r.setMetadata(metadata)

            # layer.zoom_max = "don't show when zoomed out beyond"
            zoom_max = source_layer.zoom_min or 0
            # layer.zoom_min = "don't show when zoomed in beyond"
            zoom_min = source_layer.zoom_max or 0

            enabled_scale_range = bool(zoom_max or zoom_min)
            if zoom_max and zoom_min and zoom_min < zoom_max:
                # inconsistent scale range -- zoom_max should be smaller number than zoom_min
                zoom_min, zoom_max = zoom_max, zoom_min

                # qgis minimum scale = don't show when zoomed out beyond, i.e. ArcGIS zoom_max
                r.setMinimumScale(
                    zoom_max if enabled_scale_range else source_layer.stored_zoom_max
                )
                # qgis maximum scale = don't show when zoomed in beyond, i.e. ArcGIS zoom_min
                r.setMaximumScale(
                    zoom_min if enabled_scale_range else source_layer.stored_zoom_min
                )
            r.setScaleBasedVisibility(enabled_scale_range)
        return res

    @staticmethod
    def wms_layer_to_QgsRasterLayer(
        source_layer,
        input_file: str,
        context: Context,
        fallback_crs=QgsCoordinateReferenceSystem(),
    ):
        username = ""
        base_url = source_layer.connection_name.properties.properties["URL"]
        url = QUrl(base_url)
        url_query = QUrlQuery(url.query())
        url_query.removeQueryItem("layers")
        url.setQuery(url_query)
        base_url = url.toString()

        if "USER" in source_layer.connection_name.properties.properties:
            username = source_layer.connection_name.properties.properties["USER"]
        layers = []

        def add_layer(layer):
            nonlocal layers

            layer_name = layer.name
            layer_id = layer.id
            style = ""
            if layer.style:
                style = "&styles={}".format(layer.style)
            else:
                style = "&styles"

            image_format = "image/jpeg"
            if source_layer.image_format in (WmsMapLayer.IMAGE_FORMAT_JPEG,):
                image_format = "image/jpeg"
            elif source_layer.image_format in (
                WmsMapLayer.IMAGE_FORMAT_PNG8,
                WmsMapLayer.IMAGE_FORMAT_PNG24,
                WmsMapLayer.IMAGE_FORMAT_PNG32,
            ):
                image_format = "image/png"

            if (
                context.frame_crs is not None
                and context.frame_crs.isValid()
                and context.frame_crs.authid()
            ):
                crs = "&crs={}".format(context.frame_crs.authid())
            else:
                crs = ""

            uri = ""
            if username:
                uri = "username={}&".format(username)

            this_url = base_url
            if context.upgrade_http_to_https:
                this_url = this_url.replace("http://", "https://")

            uri += "format={}{}&layers={}{}&url={}".format(
                image_format, crs, layer_id, style, this_url
            )
            options = QgsRasterLayer.LayerOptions()
            options.skipCrsValidation = True

            if context.ignore_online_sources:
                uri = ""

            uri = DatasetNameConverter.add_stored_wms_connection_params_to_uri(
                uri, context
            )
            rl = QgsRasterLayer(
                uri, source_layer.name + " " + layer_name, "wms", options
            )

            if not layer.visible:
                rl.setCustomProperty("_slyr_hidden_layer", True)

            layers.append(rl)

        def add_group(group):
            for c in group.children:
                if isinstance(c, WmsGroupLayer):
                    add_group(c)
                else:
                    add_layer(c)

        for c in source_layer.children:
            if isinstance(c, WmsGroupLayer):
                add_group(c)
            else:
                add_layer(c)

        # layer.zoom_max = "don't show when zoomed out beyond"
        zoom_max = source_layer.zoom_max or 0
        # layer.zoom_min = "don't show when zoomed in beyond"
        zoom_min = source_layer.zoom_min or 0

        enabled_scale_range = zoom_max or zoom_min
        if zoom_max and zoom_min and zoom_min > zoom_max:
            # inconsistent scale range -- zoom_max should be bigger number than zoom_min
            tmp = zoom_min
            zoom_min = zoom_max
            zoom_max = tmp

        for layer in layers:
            if layer.renderer():
                if Qgis.QGIS_VERSION_INT >= 31800:
                    layer.setOpacity(1.0 - (source_layer.transparency or 0) / 100)
                else:
                    layer.renderer().setOpacity(
                        1.0 - (source_layer.transparency or 0) / 100
                    )
            metadata = layer.metadata()
            metadata.setAbstract(source_layer.description)
            layer.setMetadata(metadata)

            if enabled_scale_range:
                # qgis minimum scale = don't show when zoomed out beyond, i.e. ArcGIS zoom_max
                layer.setMinimumScale(zoom_max)
                # qgis maximum scale = don't show when zoomed in beyond, i.e. ArcGIS zoom_min
                layer.setMaximumScale(zoom_min)
                layer.setScaleBasedVisibility(True)

        if len(layers) > 1:
            for layer in layers:
                layer.setCustomProperty("_slyr_group_name", source_layer.name)
                layer.setCustomProperty("_slyr_group_visible", source_layer.visible)
                layer.setCustomProperty("_slyr_group_expanded", False)

        return layers

    @staticmethod
    def wmts_layer_to_QgsRasterLayer(
        source_layer: WmtsLayer,
        input_file: str,
        context: Context,
        fallback_crs=QgsCoordinateReferenceSystem(),
    ):
        def get_layer(endpoint=""):
            url = source_layer.provider.get_capabilities_url
            warn_on_invalid = not url
            if not url:
                url = source_layer.provider.template_url
            else:
                if url[-1] == "?":
                    url = url[:-1]
                if endpoint:
                    url += endpoint

            if context.upgrade_http_to_https:
                url = url.replace("http://", "https://")

            crs = CrsConverter.convert_crs(source_layer.provider.crs, context)

            # dpiMode=7&
            uri = "crs={}&format={}&layers={}&styles={}&tileMatrixSet={}&url={}".format(
                crs.authid().upper(),
                source_layer.provider.format,
                source_layer.provider.layer,
                source_layer.provider.style,
                source_layer.provider.tile_matrix_set,
                urllib.parse.quote(url, safe="/:"),
            )

            if context.ignore_online_sources:
                uri = ""

            uri = DatasetNameConverter.add_stored_wms_connection_params_to_uri(
                uri, context
            )

            options = QgsRasterLayer.LayerOptions()
            options.skipCrsValidation = True
            rl = QgsRasterLayer(uri, source_layer.name, "wms", options)
            if warn_on_invalid and not rl.isValid():
                context.push_warning(
                    "QGIS requires a GetCapabilities URL for WMTS layers. The source for this layer will need to be manually repaired.",
                    level=Context.WARNING,
                )
            return rl

        rl = get_layer()
        if not rl.isValid():
            rl = get_layer("?service=wmts&request=GetCapabilities")

        if rl.renderer():
            rl.renderer().setOpacity(1.0 - (source_layer.transparency or 0) / 100)
        return [rl]

    @staticmethod
    def internet_tiled_layer_to_QgsRasterLayer(
        source_layer: InternetTiledLayer,
        input_file: str,
        context: Context,
        fallback_crs=QgsCoordinateReferenceSystem(),
    ):
        if source_layer.identifier in (
            "5107113422519f60f573b72533b09aa0",
            "5e727ad96728886fb069338b6f1ec64f",
            "maps_live_com_Aerial",
            "maps.live.com_Aerial",
        ):
            uri = "type=xyz&url=http://ecn.t3.tiles.virtualearth.net/tiles/a%7Bq%7D.jpeg?g%3D1&zmax=19&zmin=1"
        elif source_layer.identifier in (
            "1d6d773032d283aa2c1cfae98de9e5e6",
            "d274be640407080e93e07a92f8dc1f6e",
            "maps.live.com_Hybrid",
            "maps_live_com_Hybrid",
        ):
            uri = "type=xyz&url=http://ak.dynamic.t1.tiles.virtualearth.net/comp/ch/%7Bq%7D?mkt%3D{}%26it%3DA,G,L%26og%3D485%26n%3Dz&zmax=18&zmin=0".format(
                source_layer.definition.culture
            )
        elif source_layer.identifier in (
            "b2e4b9059057708ffb4f6ec0ec8a3323",
            "93bb0be37705432934e50e3c8fccb744",
            "maps_live_com_Street",
            "maps.live.com_Street",
        ):
            uri = "type=xyz&url=http://ak.dynamic.t0.tiles.virtualearth.net/comp/ch/%7Bq%7D?mkt%3D{}%26it%3DG,L%26shading%3Dhill%26og%3D485%26n%3Dz&zmax=18&zmin=0".format(
                source_layer.definition.culture
            )
        elif source_layer.identifier in (
            "dc971e70415e5f57ee2bf8200ccf3c94",
            "OpenStreetMap.org_Street",
        ):
            uri = "type=xyz&url=https://tile.openstreetmap.org/%7Bz%7D/%7Bx%7D/%7By%7D.png&zmax=19&zmin=0&dpiMode=1"
        elif source_layer.identifier in ("e6b4b9fe44f9754b85628b96f5a1813b",):
            # http://mt0.google.com/vt/lyrs=s,h&x={col}&y={row}&z={level}
            uri = "type=xyz&url=https://mt1.google.com/vt/lyrs%3Ds,h%26x%3D%7Bx%7D%26y%3D%7By%7D%26z%3D%7Bz%7D&zmax=19&zmin=0"
        elif source_layer.identifier in ("78f708b639f1455bcb34bc7f7e3fbb1b",):
            # http://mt0.google.com/vt/lyrs=s&x={col}&y={row}&z={level}
            uri = "type=xyz&url=https://mt1.google.com/vt/lyrs%3Ds%26x%3D%7Bx%7D%26y%3D%7By%7D%26z%3D%7Bz%7D&zmax=19&zmin=0"
        elif source_layer.identifier in ("df8dfb18707ade22b64e95e262ac37ab",):
            # http://mt0.google.com/vt/lyrs=m&x={col}&y={row}&z={level}
            uri = "type=xyz&url=https://mt1.google.com/vt/lyrs%3Dm%26x%3D%7Bx%7D%26y%3D%7By%7D%26z%3D%7Bz%7D&zmax=19&zmin=0"
        elif source_layer.identifier in ("9cafab5651a9664c7ae90007f12f1f51",):
            # http://mt0.google.com/vt/lyrs=y&x={col}&y={row}&z={level}
            uri = "type=xyz&url=https://mt1.google.com/vt/lyrs%3Dy%26x%3D%7Bx%7D%26y%3D%7By%7D%26z%3D%7Bz%7D&zmax=19&zmin=0"
        else:
            raise NotImplementedException(
                "Converting internet layer for {} is not yet implemented".format(
                    source_layer.identifier
                )
            )

        if context.ignore_online_sources:
            uri = ""

        uri = DatasetNameConverter.add_stored_xyz_connection_params_to_uri(uri, context)

        res = QgsRasterLayer(uri, source_layer.name, "wms")

        # layer.zoom_max = "don't show when zoomed out beyond"
        zoom_max = source_layer.zoom_max
        # layer.zoom_min = "don't show when zoomed in beyond"
        zoom_min = source_layer.zoom_min

        enabled_scale_range = zoom_max or zoom_min
        if zoom_max and zoom_min and zoom_min > zoom_max:
            # inconsistent scale range -- zoom_max should be bigger number than zoom_min
            tmp = zoom_min
            zoom_min = zoom_max
            zoom_max = tmp

        if enabled_scale_range:
            # qgis minimum scale = don't show when zoomed out beyond, i.e. ArcGIS zoom_max
            res.setMinimumScale(zoom_max)
            # qgis maximum scale = don't show when zoomed in beyond, i.e. ArcGIS zoom_min
            res.setMaximumScale(zoom_min)
            res.setScaleBasedVisibility(True)
        return res
