"""
Extract hyperlinks from layers to tables algorithm
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
)

from .algorithm import SlyrAlgorithm


class ExtractHyperlinksToTables(SlyrAlgorithm):
    """
    Extracts hyperlinks from layers to tables
    """

    INPUT = "INPUT"
    OUTPUT = "OUTPUT"

    # pylint: disable=missing-docstring,unused-argument

    def createInstance(self):
        return ExtractHyperlinksToTables()

    def name(self):
        return "extracthyperlinks"

    def displayName(self):
        return "Extract hyperlinks to tables"

    def shortDescription(self):
        return "Extract hyperlinks from layers to standalone tables"

    def group(self):
        return "Hyperlinks"

    def groupId(self):
        return "hyperlinks"

    def shortHelpString(self):
        return "Extract hyperlinks from layers to standalone tables"

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFile(
                self.INPUT,
                "Input MXD/MXT/PMF/LYR file",
                fileFilter="MXD/MXT/PMF/LYR Documents (*.mxd *.MXD *.mxt *.MXT *.pmf *.PMF *.lyr *.LYR)",
            )
        )

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT, "Destination GeoPackage", fileFilter="GPKG files (*.gpkg)"
            )
        )

    def autogenerateParameterValues(self, rowParameters, changedParameter, mode):
        if changedParameter == self.INPUT:
            input_file = rowParameters.get(self.INPUT)
            if input_file:
                input_path = Path(input_file)
                if input_path.exists():
                    return {self.OUTPUT: input_path.with_suffix(".gpkg").as_posix()}

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
