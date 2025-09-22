"""
Converts .stylx databases to GPL color palette files
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
    QgsProcessingOutputNumber,
    QgsProcessingException,
)

from .algorithm import SlyrAlgorithm


class StylxToGpl(SlyrAlgorithm):
    """
    Converts .stylx databases to GPL color palette files
    """

    INPUT = "INPUT"
    OUTPUT = "OUTPUT"

    COLOR_COUNT = "COLOR_COUNT"
    UNREADABLE_COLOR_COUNT = "UNREADABLE_COLOR_COUNT"

    # pylint: disable=missing-docstring,unused-argument

    def createInstance(self):
        return StylxToGpl()

    def name(self):
        return "stylxtogpl"

    def displayName(self):
        return "Convert STYLX to GPL color palette"

    def shortDescription(self):
        return "Converts ArcGIS Pro STYLX database to a GPL format color palette file."

    def group(self):
        return "ArcGIS Pro"

    def groupId(self):
        return "arcgispro"

    def shortHelpString(self):
        return (
            "Converts an ArcGIS Pro STYLX database to a GPL "
            "format color palette file, extracting all color entities "
            "saved in the style."
        )

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFile(self.INPUT, "Stylx database", extension="stylx")
        )

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT, "Destination GPL file", fileFilter="GPL files (*.gpl)"
            )
        )

        self.addOutput(QgsProcessingOutputNumber(self.COLOR_COUNT, "Color Count"))
        self.addOutput(
            QgsProcessingOutputNumber(
                self.UNREADABLE_COLOR_COUNT, "Unreadable Color Count"
            )
        )

    def autogenerateParameterValues(self, rowParameters, changedParameter, mode):
        if changedParameter == self.INPUT:
            input_file = rowParameters.get(self.INPUT)
            if input_file:
                input_path = Path(input_file)
                if input_path.exists():
                    return {self.OUTPUT: input_path.with_suffix(".gpl").as_posix()}

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
