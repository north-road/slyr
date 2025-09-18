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
SLYR QGIS Processing algorithms
"""

from qgis.core import (
    QgsProcessingParameterFile,
    QgsProcessingParameterFileDestination,
    QgsProcessingOutputNumber,
    QgsProcessingException,
)

from .algorithm import SlyrAlgorithm


class GplToStylx(SlyrAlgorithm):
    """
    Converts GPL color palette files to .stylx databases
    """

    INPUT = "INPUT"
    OUTPUT = "OUTPUT"

    COLOR_COUNT = "COLOR_COUNT"

    # pylint: disable=missing-docstring,unused-argument

    def createInstance(self):
        return GplToStylx()

    def name(self):
        return "gpltostlyx"

    def displayName(self):
        return "Convert GPL color palette to stylx"

    def shortDescription(self):
        return "Convert a GPL color palette to an ArcGIS Pro stylx database"

    def group(self):
        return "ArcGIS Pro"

    def groupId(self):
        return "arcgispro"

    def shortHelpString(self):
        return (
            "Converts a GPL format color palette file to an ArcGIS Pro stylx database."
        )

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFile(self.INPUT, "GPL palette", extension="gpl")
        )

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT,
                "Destination stylx database",
                fileFilter="STYLX files (*.stylx)",
            )
        )

        self.addOutput(QgsProcessingOutputNumber(self.COLOR_COUNT, "Color Count"))

    def processAlgorithm(
        self,  # pylint: disable=too-many-locals,too-many-statements
        parameters,
        context,
        feedback,
    ):
        raise QgsProcessingException(
            "This algorithm is available in the licensed version of SLYR only - please see https://north-road.com/slyr/ for details"
        )

    # pylint: enable=missing-docstring,unused-argument
