"""
Converts an MAPX document to a QGS project file
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
from pathlib import Path

from qgis.core import (
    Qgis,
    QgsProject,
    QgsProcessingParameterFile,
    QgsProcessingParameterFileDestination,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterDefinition,
)

from .algorithm import SlyrAlgorithm
from ...converters.context import Context

from qgis.core import QgsProcessingException


class ConvertQgsToMapx(SlyrAlgorithm):
    """
    Converts a QGS project file to a MAPX Document
    """

    INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    TEST_MODE = "TEST_MODE"

    # pylint: disable=missing-docstring,unused-argument

    def createInstance(self):
        return ConvertQgsToMapx()

    def name(self):
        return "convertqgstomapx"

    def displayName(self):
        return "Convert QGS to MAPX"

    def shortDescription(self):
        return "Converts a QGIS project file as a MAPX file."

    def group(self):
        return "ArcGIS Pro"

    def groupId(self):
        return "arcgispro"

    def shortHelpString(self):
        return "Converts a QGIS project file as a MAPX."

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFile(
                self.INPUT,
                "Input QGS file",
                fileFilter="QGS Documents (*.qgs *.QGS *.qgz *.QGZ)",
            )
        )

        param_test_mode = QgsProcessingParameterBoolean(
            self.TEST_MODE, "Test mode (debug option)", False, True
        )
        param_test_mode.setFlags(
            param_test_mode.flags() | QgsProcessingParameterDefinition.Flag.FlagHidden
        )
        self.addParameter(param_test_mode)

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT,
                "Destination MAPX project file",
                fileFilter="MAPX files (*.mapx)",
            )
        )

    def autogenerateParameterValues(self, rowParameters, changedParameter, mode):
        if changedParameter == self.INPUT:
            input_file = rowParameters.get(self.INPUT)
            if input_file:
                input_path = Path(input_file)
                if input_path.exists():
                    return {self.OUTPUT: input_path.with_suffix(".mapx").as_posix()}

        return {}

    def processAlgorithm(self, parameters, context, feedback):
        raise QgsProcessingException(
            "This algorithm is available in the licensed version of SLYR only - please see https://north-road.com/slyr/ for details"
        )
