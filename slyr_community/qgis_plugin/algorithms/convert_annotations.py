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
Converts annotations in a binary column to a QGIS annotation layer
"""

from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingParameterVectorLayer,
    QgsProcessingParameterField,
    QgsProcessingException,
)

from .algorithm import SlyrAlgorithm


class ConvertAnnotations(SlyrAlgorithm):
    """
    Converts annotations in a binary column
    """

    INPUT = "INPUT"
    FIELD = "FIELD"
    OUTPUT = "OUTPUT"

    # pylint: disable=missing-docstring,unused-argument

    def createInstance(self):
        return ConvertAnnotations()

    def name(self):
        return "convertannotations"

    def displayName(self):
        return "Convert annotations (beta)"

    def shortDescription(self):
        return ""

    def flags(self):
        return super().flags() | QgsProcessingAlgorithm.FlagNoThreading

    def group(self):
        return "Annotations"

    def groupId(self):
        return "annotations"

    def shortHelpString(self):
        return ""

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer(self.INPUT, "Input layer"))

        self.addParameter(
            QgsProcessingParameterField(
                self.FIELD,
                "Element field",
                defaultValue="ELEMENT",
                parentLayerParameterName=self.INPUT,
            )
        )

    def processAlgorithm(
        self,  # pylint: disable=too-many-locals,too-many-statements,too-many-branches
        parameters,
        context,
        feedback,
    ):
        raise QgsProcessingException(
            "This algorithm is available in the licensed version of SLYR only - please see https://north-road.com/slyr/ for details"
        )

    # pylint: enable=missing-docstring,unused-argument
