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
from collections import defaultdict

from qgis.core import (
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
from .symbols import SymbolConverter
from .utils import ConversionUtils

from ..parser.objects.function_raster_dataset_name import FunctionRasterDatasetName
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

        if isinstance(layer.dataset_name, RasterBandName):
            dataset_name = layer.dataset_name.dataset_name
            band = layer.dataset_name.band
        else:
            dataset_name = layer.dataset_name
            band = -1

        if isinstance(dataset_name, (SdeRasterDatasetName, FgdbRasterDatasetName)):
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
            if isinstance(renderer, RasterClassifyColorRampRenderer):
                raster_min = renderer.breaks[0]
                raster_max = renderer.breaks[-1]
            else:
                raster_min = renderer.minimum_break or 0
                raster_max = renderer.class_breaks[-1].upper_bound or 0

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
            if isinstance(renderer, RasterClassifyColorRampRenderer):
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
            else:
                for i, b in enumerate(renderer.class_breaks):
                    items.append(
                        QgsColorRampShader.ColorRampItem(
                            b.upper_bound or 0,
                            ColorConverter.color_to_qcolor(b.color),
                            b.label,
                        )
                    )
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
