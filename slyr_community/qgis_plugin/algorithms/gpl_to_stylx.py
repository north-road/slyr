"""
SLYR QGIS Processing algorithms
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
from pathlib import Path
from shutil import copyfile

from qgis.PyQt.QtCore import QFile
from qgis.core import (
    QgsProcessingParameterFile,
    QgsProcessingParameterFileDestination,
    QgsProcessingOutputNumber,
    QgsProcessingException,
    QgsFeature,
    QgsVectorLayer,
    QgsSymbolLayerUtils,
)

from .algorithm import SlyrAlgorithm
from ...converters.color import ColorConverter


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
        return "Convert GPL color palette to STYLX"

    def shortDescription(self):
        return "Convert a GPL color palette to an ArcGIS Pro STYLX database"

    def group(self):
        return "ArcGIS Pro"

    def groupId(self):
        return "arcgispro"

    def shortHelpString(self):
        return (
            "Converts a GPL format color palette file to an ArcGIS Pro STYLX database."
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

    def autogenerateParameterValues(self, rowParameters, changedParameter, mode):
        if changedParameter == self.INPUT:
            input_file = rowParameters.get(self.INPUT)
            if input_file:
                input_path = Path(input_file)
                if input_path.exists():
                    return {self.OUTPUT: input_path.with_suffix(".stylx").as_posix()}

        return {}

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
