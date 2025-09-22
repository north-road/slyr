"""
Converts QGIS xml style databases to a stylx database
"""

# /***************************************************************************
#  *                                                                         *
#  *   This program is free software; you can redistribute it and/or modify  *
#  *   it under the terms of the GNU General Public License as published by  *
#  *   the Free Software Foundation; either version 2 of the License, or     *
#  *   (at your option) any later version.                                   *
#  *                                                                         *
#  ***************************************************************************/

import os
from pathlib import Path

from qgis.core import (
    QgsProcessingParameterFile,
    QgsProcessingParameterFileDestination,
    QgsProcessingOutputNumber,
    QgsProcessingException,
    QgsStyle,
)

from .algorithm import SlyrAlgorithm
from .utils import AlgorithmUtils
from qgis.core import QgsProcessingException


class XmlToStylx(SlyrAlgorithm):
    """
    Converts QGIS xml style databases to a stylx database
    """

    INPUT = "INPUT"
    OUTPUT = "OUTPUT"

    COLOR_RAMP_COUNT = "COLOR_RAMP_COUNT"
    SYMBOL_COUNT = "SYMBOL_COUNT"
    TEXT_SYMBOL_COUNT = "TEXT_SYMBOL_COUNT"

    # pylint: disable=missing-docstring,unused-argument

    def createInstance(self):
        return XmlToStylx()

    def name(self):
        return "xmltostylx"

    def displayName(self):
        return "Convert QGIS style XML to STYLX"

    def shortDescription(self):
        return "Convert a QGIS XML style database to an ArcGIS Pro STYLX database"

    def group(self):
        return "ArcGIS Pro"

    def groupId(self):
        return "arcgispro"

    def shortHelpString(self):
        return "Converts a QGIS XML style database to an ArcGIS Pro STYLX database."

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFile(self.INPUT, "Style XML", extension="xml")
        )

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT,
                "Destination stylx database",
                fileFilter="STYLX files (*.stylx)",
            )
        )

        self.addOutput(
            QgsProcessingOutputNumber(self.COLOR_RAMP_COUNT, "Color Ramp Count")
        )
        self.addOutput(QgsProcessingOutputNumber(self.SYMBOL_COUNT, "Symbol Count"))
        self.addOutput(
            QgsProcessingOutputNumber(self.TEXT_SYMBOL_COUNT, "Text Symbol Count")
        )

    def autogenerateParameterValues(self, rowParameters, changedParameter, mode):
        if changedParameter == self.INPUT:
            input_file = rowParameters.get(self.INPUT)
            if input_file:
                input_path = Path(input_file)
                if input_path.exists():
                    return {self.OUTPUT: input_path.with_suffix(".stylx").as_posix()}

        return {}

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
