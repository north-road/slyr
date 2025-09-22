"""
Base class for SLYR algorithms
"""

# /***************************************************************************
#  *                                                                         *
#  *   This program is free software; you can redistribute it and/or modify  *
#  *   it under the terms of the GNU General Public License as published by  *
#  *   the Free Software Foundation; either version 2 of the License, or     *
#  *   (at your option) any later version.                                   *
#  *                                                                         *
#  ***************************************************************************/

import json
import os
import pathlib
from typing import Optional
from collections import defaultdict
from shutil import copyfile

from qgis.PyQt.QtCore import QDir, QVariant

from qgis.core import (
    Qgis,
    QgsWkbTypes,
    QgsProviderRegistry,
    QgsDataProvider,
    QgsVectorLayer,
    QgsVectorFileWriter,
    QgsSettings,
    QgsProcessingMultiStepFeedback,
    QgsProject,
    QgsProcessingFeedback,
    QgsMapLayer,
    QgsStyle,
    QgsProcessingException,
    QgsFeature,
)

from ...converters.utils import ConversionUtils
from ...parser.object import Object
from ...converters.text_format import TextSymbolConverter
from ...converters.color_ramp import ColorRampConverter
from ...converters.context import Context
from ...parser.exceptions import NotImplementedException


class ConversionResults:
    """
    Storage for results of a conversion
    """

    def __init__(self):
        self.layer_map = {}
        self.created_databases = set()


class AlgorithmUtils:
    """
    Utility functions for SLYR algorithms
    """

    @staticmethod
    def should_convert_layer(layer) -> bool:
        """
        Returns True if a layer is a non-open standard and should be converted
        """
        source = QgsProviderRegistry.instance().decodeUri(
            layer.providerType(), layer.source()
        )
        if "path" in source and source["path"]:
            path = pathlib.Path(source["path"])

            if path.suffix.lower() in (".gdb", ".mdb"):
                return True

        return False

    @staticmethod
    def convert_vector_layer(
        layer,  # pylint: disable=too-many-locals,too-many-branches,too-many-statements
        project,
        data_folder: str,
        feedback,
        conversion_results: ConversionResults,
        change_source_on_error: bool = False,
        verbose_log=False,
    ):
        """
        Converts a vector layer to a standard format
        """
        if layer.customProperty("original_uri"):
            uri = layer.customProperty("original_uri")
            if verbose_log:
                feedback.pushDebugInfo(
                    f"Original layer URI from custom properties is {uri}"
                )
        else:
            uri = layer.source()
            if verbose_log:
                feedback.pushDebugInfo(
                    "Original layer URI not found in custom properties"
                )

        original_crs = layer.crs()

        source = QgsProviderRegistry.instance().decodeUri(layer.providerType(), uri)
        if verbose_log:
            feedback.pushInfo("")

        # older versions of QGIS didn't correctly strip out the subset from the layerName:
        if "subset" not in source:
            if "|subset=" in source["layerName"]:
                if verbose_log:
                    feedback.pushDebugInfo(
                        "Stripping out subset string from layerName: {}".format(
                            source["layerName"]
                        )
                    )
                layer_name = source["layerName"]
                parts = layer_name.split("|subset=")
                if len(parts) == 2:
                    source["layerName"] = parts[0]
                    if verbose_log:
                        feedback.pushDebugInfo(
                            "Cleaned layer name: {}".format(source["layerName"])
                        )
                elif verbose_log:
                    feedback.reportError("Failed to strip subset string!")
            elif "|subset=" in source["path"]:
                path = source["path"]
                if verbose_log:
                    feedback.pushDebugInfo(
                        "Stripping out subset string from path: {}".format(
                            source["path"]
                        )
                    )
                parts = path.split("|subset=")
                if len(parts) == 2:
                    source["path"] = parts[0]
                    if verbose_log:
                        feedback.pushDebugInfo(
                            "Cleaned path: {}".format(source["path"])
                        )
                elif verbose_log:
                    feedback.reportError("Failed to strip subset string!")

        # convert to Geopackage
        source_uri = QgsProviderRegistry.instance().encodeUri(
            layer.providerType(),
            {"path": source["path"], "layerName": source["layerName"]},
        )

        # Sometimes the case varies in ArcMap documents, so when comparing to previously converted layers
        # we use a case-insensitive path/layername which is normalized
        result_key = QgsProviderRegistry.instance().encodeUri(
            layer.providerType(),
            {
                "path": pathlib.Path(source["path"]).resolve().as_posix().lower(),
                "layerName": source["layerName"].lower(),
            },
        )

        if verbose_log:
            feedback.pushDebugInfo(
                "Converting layer: {} ( {} )".format(
                    source["path"], source["layerName"]
                )
            )
            feedback.pushDebugInfo(f"Cached result key: {result_key}")

        provider_options = QgsDataProvider.ProviderOptions()
        provider_options.transformContext = project.transformContext()
        subset = layer.subsetString()

        # have we maybe already converted this layer??
        if result_key in conversion_results.layer_map:
            previous_results = conversion_results.layer_map[result_key]
            if previous_results.get("error"):
                if verbose_log:
                    feedback.pushDebugInfo(
                        "Already tried to convert this layer, but failed last time, skipping..."
                    )
                    feedback.pushDebugInfo("Restoring stored URI")

                layer.setDataSource(uri, layer.name(), "ogr", provider_options)
            else:
                if verbose_log:
                    feedback.pushDebugInfo(
                        "Already converted this layer, reusing previous converted path: {} layername: {}".format(
                            previous_results["destPath"], previous_results["destLayer"]
                        )
                    )

                layer.setDataSource(
                    QgsProviderRegistry.instance().encodeUri(
                        "ogr",
                        {
                            "path": previous_results["destPath"],
                            "layerName": previous_results["destLayer"],
                        },
                    ),
                    layer.name(),
                    "ogr",
                    provider_options,
                )
                if verbose_log:
                    feedback.pushDebugInfo(
                        "new source {}".format(layer.dataProvider().dataSourceUri())
                    )
            if subset:
                if verbose_log:
                    feedback.pushDebugInfo("Resetting subset string: {}".format(subset))
                layer.setSubsetString(subset)

            layer.setCrs(original_crs)
            return previous_results

        source_layer = QgsVectorLayer(source_uri, "", layer.providerType())

        path = pathlib.Path(source["path"])

        dest_file_name = (
            (pathlib.Path(data_folder) / path.stem).with_suffix(".gpkg")
        ).as_posix()
        if dest_file_name not in conversion_results.created_databases:
            # about to use a new file -- let's double-check that it doesn't already exist. We don't want
            # to put layers into a database which we didn't make for this project
            counter = 1
            while pathlib.Path(dest_file_name).exists():
                counter += 1
                dest_file_name = (
                    (
                        pathlib.Path(data_folder) / (path.stem + "_" + str(counter))
                    ).with_suffix(".gpkg")
                ).as_posix()
                if dest_file_name in conversion_results.created_databases:
                    break

            if verbose_log:
                feedback.pushDebugInfo(
                    "Creating new destination file {}".format(dest_file_name)
                )
        elif verbose_log:
            feedback.pushDebugInfo(
                "Reusing existing destination file {}".format(dest_file_name)
            )

        # now this filename is ok for other layers to be stored in for this conversion
        conversion_results.created_databases.add(dest_file_name)

        layer_name_candidate = source["layerName"]
        counter = 1
        while QgsVectorFileWriter.targetLayerExists(
            dest_file_name, layer_name_candidate
        ):
            counter += 1
            layer_name_candidate = "{}_{}".format(source["layerName"], counter)

        if verbose_log:
            feedback.pushDebugInfo(
                "Target layer name is {}".format(layer_name_candidate)
            )

        if not source_layer.isValid():
            if verbose_log:
                feedback.reportError("Source layer is not valid")
            if path.exists():
                if verbose_log:
                    feedback.pushDebugInfo("File path DOES exist")

                    test_layer = QgsVectorLayer(path.as_posix())
                    sub_layers = test_layer.dataProvider().subLayers()
                    feedback.pushDebugInfo(
                        f'Readable layers from "{path.as_posix()}" are:'
                    )
                    for sub_layer in sub_layers:
                        _, name, count, geom_type, _, _ = sub_layer.split(
                            QgsDataProvider.sublayerSeparator()
                        )
                        feedback.pushDebugInfo(
                            f'- "{name}" ({count} features, geometry type {geom_type})'
                        )

            if path.exists() and path.suffix.lower() == ".mdb":
                try:
                    source["layerName"].encode("ascii")
                except UnicodeDecodeError:
                    error = f'''MDB layers with unicode names are not supported by QGIS -- cannot convert "{source["layerName"]}"'''
                    if verbose_log:
                        feedback.reportError(error)
                        feedback.pushDebugInfo("Restoring stored URI")

                    layer.setDataSource(uri, layer.name(), "ogr", provider_options)
                    if subset:
                        if verbose_log:
                            feedback.pushDebugInfo(
                                "Resetting subset string: {}".format(subset)
                            )
                        layer.setSubsetString(subset)

                    layer.setCrs(original_crs)
                    conversion_results.layer_map[result_key] = {"error": error}
                    return conversion_results.layer_map[result_key]

                # maybe a non-spatial table, which can't be read with GDAL < 3.2
                source_layer = None

                if verbose_log:
                    feedback.pushDebugInfo(
                        "Layer type is {}".format(
                            QgsWkbTypes.displayString(layer.wkbType())
                        )
                    )

                if layer.wkbType() == QgsWkbTypes.Type.NoGeometry:
                    if verbose_log:
                        feedback.pushDebugInfo(
                            "Attempting fallback for non-spatial tables"
                        )
                    try:
                        source_layer = (
                            ConversionUtils.convert_mdb_table_to_memory_layer(
                                str(path), source["layerName"]
                            )
                        )
                        if verbose_log:
                            feedback.pushDebugInfo("Fallback succeeded!")
                    except Exception as e:  # nopep8, pylint: disable=broad-except
                        if verbose_log:
                            feedback.reportError("Fallback failed: {}".format(str(e)))
                        source_layer = None
                elif verbose_log:
                    feedback.reportError("Nothing else to try, conversion failed")

                if not source_layer:
                    # here we fake things. We don't leave the original path to the mdb layer intact in the converted
                    # project, as this can cause massive issues with QGIS as it attempts to re-read this path constantly
                    # rather we "pretend" that the conversion was ok and set the broken layer's path to what the gpkg
                    # converted version WOULD have been! It'll still be broken in the converted project (obviously),
                    # but QGIS will no longer try endless to read the MDB and get all hung up on this...
                    conversion_results.layer_map[result_key] = {
                        "sourcePath": source["path"],
                        "sourceLayer": source["layerName"],
                        "destPath": dest_file_name,
                        "destLayer": layer_name_candidate,
                        "error": "Could not open {} ({}) for conversion".format(
                            source_uri, source["layerName"]
                        ),
                    }

                    if change_source_on_error:
                        if verbose_log:
                            feedback.pushDebugInfo("Restoring stored URI")

                        layer.setDataSource(uri, layer.name(), "ogr", provider_options)
                        if subset:
                            if verbose_log:
                                feedback.pushDebugInfo(
                                    "Resetting subset string: {}".format(subset)
                                )
                            layer.setSubsetString(subset)
                        if verbose_log:
                            feedback.pushDebugInfo(
                                "new source {}".format(
                                    layer.dataProvider().dataSourceUri()
                                )
                            )

                        layer.setCrs(original_crs)

                    return conversion_results.layer_map[result_key]
            else:
                if not path.exists():
                    error = "The referenced file {} does NOT exist!".format(str(path))
                else:
                    error = "The referenced file exists, but could not open {} ({}) for conversion".format(
                        source_uri, source["layerName"]
                    )

                if verbose_log:
                    feedback.reportError(error)
                    feedback.pushDebugInfo("Restoring stored URI")

                layer.setDataSource(uri, layer.name(), "ogr", provider_options)
                if subset:
                    if verbose_log:
                        feedback.pushDebugInfo(
                            "Resetting subset string: {}".format(subset)
                        )
                    layer.setSubsetString(subset)

                layer.setCrs(original_crs)
                conversion_results.layer_map[result_key] = {"error": error}
                return conversion_results.layer_map[result_key]

        if verbose_log:
            feedback.pushDebugInfo("Source is valid, converting")

        options = QgsVectorFileWriter.SaveVectorOptions()

        options.layerName = layer_name_candidate
        options.actionOnExistingFile = (
            QgsVectorFileWriter.ActionOnExistingFile.CreateOrOverwriteLayer
            if pathlib.Path(dest_file_name).exists()
            else QgsVectorFileWriter.ActionOnExistingFile.CreateOrOverwriteFile
        )
        options.feedback = feedback
        options.layerOptions = ["GEOMETRY_NAME=Shape"]

        if Qgis.QGIS_VERSION_INT >= 33000:
            options.includeConstraints = True

        # check if we can safely use an existing FID field, or if it has to be dropped
        attributes_list = []
        for field_index, field in enumerate(source_layer.fields()):
            if field.name().lower() == "fid":
                if field.type() not in (QVariant.Int, QVariant.LongLong):
                    # FID not compatible with geopackage, skip it
                    continue

            attributes_list.append(field_index)
        options.attributes = attributes_list[:]
        if not attributes_list:
            options.skipAttributeCreation = True

        if Qgis.QGIS_VERSION_INT >= 32000:
            options.saveMetadata = True
            options.layerMetadata = source_layer.metadata()
            error, error_message, new_filename, new_layername = (
                QgsVectorFileWriter.writeAsVectorFormatV3(
                    source_layer, dest_file_name, project.transformContext(), options
                )
            )
        else:
            error, error_message = QgsVectorFileWriter.writeAsVectorFormatV2(
                source_layer, dest_file_name, project.transformContext(), options
            )
            new_filename = dest_file_name
            new_layername = options.layerName

        if error != QgsVectorFileWriter.WriterError.NoError:
            if verbose_log:
                feedback.reportError("Failed: {}".format(error_message))
                feedback.pushDebugInfo("Restoring stored URI")

            layer.setDataSource(uri, layer.name(), "ogr", provider_options)
            if subset:
                if verbose_log:
                    feedback.pushDebugInfo("Resetting subset string: {}".format(subset))
                layer.setSubsetString(subset)

            layer.setCrs(original_crs)
            conversion_results.layer_map[result_key] = {"error": error_message}
            return conversion_results.layer_map[result_key]

        if verbose_log:
            feedback.pushDebugInfo("Success!")

        provider_options = QgsDataProvider.ProviderOptions()
        provider_options.transformContext = project.transformContext()
        subset = layer.subsetString()
        layer.setDataSource(
            QgsProviderRegistry.instance().encodeUri(
                "ogr", {"path": new_filename, "layerName": new_layername}
            ),
            layer.name(),
            "ogr",
            provider_options,
        )
        if subset:
            if verbose_log:
                feedback.pushDebugInfo("Resetting subset string: {}".format(subset))
            layer.setSubsetString(subset)

        layer.setCrs(original_crs)
        if verbose_log:
            feedback.pushDebugInfo(
                "new source {}".format(layer.dataProvider().dataSourceUri())
            )

        conversion_results.layer_map[result_key] = {
            "sourcePath": source["path"],
            "sourceLayer": source["layerName"],
            "destPath": new_filename,
            "destLayer": new_layername,
        }

        return conversion_results.layer_map[result_key]

    @staticmethod
    def make_json_safe_dict(obj):
        """
        Makes a dictionary object safe for JSON storage
        """
        if isinstance(obj, dict):
            return {
                key: AlgorithmUtils.make_json_safe_dict(value)
                for key, value in obj.items()
            }
        elif isinstance(obj, list):
            return [AlgorithmUtils.make_json_safe_dict(value) for value in obj]
        elif isinstance(obj, bytes):
            return str(obj)
        elif issubclass(obj.__class__, Object):
            return str(obj)
        else:
            return obj
