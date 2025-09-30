"""
Converts a PMF document to a QGS project file
"""

# /***************************************************************************
#  *                                                                         *
#  *   This program is free software; you can redistribute it and/or modify  *
#  *   it under the terms of the GNU General Public License as published by  *
#  *   the Free Software Foundation; either version 2 of the License, or     *
#  *   (at your option) any later version.                                   *
#  *                                                                         *
#  ***************************************************************************/

from pathlib import Path

from qgis.core import (
    QgsProcessingParameterFile,
    QgsProcessingParameterFileDestination,
    QgsProcessingException,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterDefinition,
)

from .algorithm import SlyrAlgorithm


class ConvertPmfToQgs(SlyrAlgorithm):
    """
    Converts a PMF document to a QGS project file
    """

    INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    TEST_MODE = "TEST_MODE"

    # pylint: disable=missing-docstring,unused-argument

    def createInstance(self):
        return ConvertPmfToQgs()

    def name(self):
        return "convertpmftoqgs"

    def displayName(self):
        return "Convert PMF to QGS"

    def shortDescription(self):
        return "Converts a PMF document file to a QGIS project file."

    def group(self):
        return "PMF published maps"

    def groupId(self):
        return "pmf"

    def shortHelpString(self):
        return "Converts a PMF document file to a QGIS project file."

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFile(self.INPUT, "Input PMF file", extension="pmf")
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
                "Destination QGS project file",
                fileFilter="QGS files (*.qgs);;QGZ files (*.qgz)",
            )
        )

    def autogenerateParameterValues(self, rowParameters, changedParameter, mode):
        if changedParameter == self.INPUT:
            input_file = rowParameters.get(self.INPUT)
            if input_file:
                input_path = Path(input_file)
                if input_path.exists():
                    return {self.OUTPUT: input_path.with_suffix(".qgs").as_posix()}

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
