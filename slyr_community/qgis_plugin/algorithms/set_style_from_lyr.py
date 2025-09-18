# -*- coding: utf-8 -*-

# /***************************************************************************
# context.py
# ----------
# Date                 : September 2019
# copyright            : (C) 2019 by Nyall Dawson, North Road Consulting
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
Sets a layer's style from a lyr file
"""

from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingParameterFile,
    QgsProcessingParameterVectorLayer,
    QgsProcessingException,
)

from .algorithm import SlyrAlgorithm
from ...converters.context import Context
from ...converters.layers import LayerConverter
from ...converters.vector_renderer import VectorRendererConverter
from ...parser.objects.group_layer import GroupLayer
from ...parser.stream import Stream
from ...parser.exceptions import RequiresLicenseException


class StyleFromLyr(SlyrAlgorithm):
    """
    Sets a layer's style from a lyr file
    """

    LAYER = "LAYER"
    LYR_FILE = "LYR_FILE"

    # pylint: disable=missing-docstring,unused-argument

    def createInstance(self):
        return StyleFromLyr()

    def name(self):
        return "stylefromlyr"

    def displayName(self):
        return "Set style from LYR file"

    def shortDescription(self):
        return "Sets a layer's settings and symbology from an ESRI LYR file"

    def group(self):
        return "LYR datasets"

    def groupId(self):
        return "lyr"

    def shortHelpString(self):
        return "Sets a layer's settings and symbology from an ESRI LYR file"

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterVectorLayer(self.LAYER, "Destination layer")
        )

        self.addParameter(
            QgsProcessingParameterFile(self.LYR_FILE, "LYR file", extension="lyr")
        )

    def flags(self):
        return super().flags() | QgsProcessingAlgorithm.FlagNoThreading

    def processAlgorithm(
        self,  # pylint: disable=too-many-locals,too-many-statements
        parameters,
        context,
        feedback,
    ):
        layer = self.parameterAsVectorLayer(parameters, self.LAYER, context)
        input_file = self.parameterAsString(parameters, self.LYR_FILE, context)

        conversion_context = Context()
        conversion_context.project = context.project()
        # context.style_folder, _ = os.path.split(output_file)

        with open(input_file, "rb") as f:
            stream = Stream(f, False, force_layer=True, offset=-1)
            try:
                feature_layer = stream.read_object()
            except RequiresLicenseException as e:
                raise QgsProcessingException(
                    "{} - please see https://north-road.com/slyr/ for details".format(e)
                ) from e

            if isinstance(feature_layer, GroupLayer):
                feedback.reportError(
                    "LYR files containing groups cannot be used with this algorithm",
                    fatalError=True,
                )
                return {}

            if not LayerConverter.is_layer(feature_layer):
                raise QgsProcessingException("Could not read LYR")

            renderer = VectorRendererConverter.convert_renderer(
                feature_layer.renderer, feature_layer, conversion_context
            )
            if renderer:
                layer.setRenderer(renderer)
                layer.triggerRepaint()

        return {}

    # pylint: enable=missing-docstring,unused-argument
