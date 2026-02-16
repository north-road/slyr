"""
Converts .lpkx to QLR
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
    QgsProcessingParameterBoolean,
    QgsProcessingParameterDefinition,
    QgsProcessingOutputString,
    QgsProcessingException,
)

from .algorithm import SlyrAlgorithm

try:
    from qgis.core import QgsProcessingOutputBoolean  # pylint: disable=ungrouped-imports
except ImportError:
    QgsProcessingOutputBoolean = None


class LpkxToQlr(SlyrAlgorithm):
    """
    Converts .lpkx to QLR
    """

    INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    USE_RELATIVE_PATHS = "USE_RELATIVE_PATHS"
    TEST_MODE = "TEST_MODE"
    CONVERTED = "CONVERTED"
    ERROR = "ERROR"

    # pylint: disable=missing-docstring,unused-argument

    def createInstance(self):
        return LpkxToQlr()

    def name(self):
        return "lpkxtoqlr"

    def displayName(self):
        return "Convert LPKX to QLR"

    def shortDescription(self):
        return "Converts an ArcGIS Pro LPKX layer package to a QGIS QLR file"

    def group(self):
        return "ArcGIS Pro"

    def groupId(self):
        return "arcgispro"

    def shortHelpString(self):
        return "Converts an ArcGIS Pro LPKX layer package to a QGIS QLR file"

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFile(self.INPUT, "Input LPKX file", extension="lpkx")
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.USE_RELATIVE_PATHS, "Store relative paths", defaultValue=False
            )
        )

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT, "Destination QLR file", fileFilter="QLR files (*.qlr)"
            )
        )

        param_test_mode = QgsProcessingParameterBoolean(
            self.TEST_MODE, "Test mode (debug option)", False, True
        )
        param_test_mode.setFlags(
            param_test_mode.flags() | QgsProcessingParameterDefinition.Flag.FlagHidden
        )
        self.addParameter(param_test_mode)

        if QgsProcessingOutputBoolean is not None:
            self.addOutput(QgsProcessingOutputBoolean(self.CONVERTED, "Converted"))
        self.addOutput(QgsProcessingOutputString(self.ERROR, "Error message"))

    def autogenerateParameterValues(self, rowParameters, changedParameter, mode):
        if changedParameter == self.INPUT:
            input_file = rowParameters.get(self.INPUT)
            if input_file:
                input_path = Path(input_file)
                if input_path.exists():
                    return {self.OUTPUT: input_path.with_suffix(".qlr").as_posix()}

        return {}

    def processAlgorithm(
        self,  # pylint: disable=too-many-locals,too-many-statements,too-many-return-statements
        parameters,
        context,
        feedback,
    ):
        raise QgsProcessingException(
            "This algorithm is available in the licensed version of SLYR only - please see https://north-road.com/slyr/ for details"
        )

    # pylint: enable=missing-docstring,unused-argument
