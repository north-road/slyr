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

from pathlib import Path

from qgis.core import QgsProcessingParameterFile, QgsProcessingException

from .arcpro_to_qgs import ConvertArcProToQgs


class ConvertMapxToQgs(ConvertArcProToQgs):
    """
    Converts an MAPX document to a QGS project file
    """

    # pylint: disable=missing-docstring,unused-argument

    def createInstance(self):
        return ConvertMapxToQgs()

    def name(self):
        return "convertmapxtoqgs"

    def displayName(self):
        return "Convert MAPX to QGS"

    def shortDescription(self):
        return "Converts a MAPX document file to a QGS project file."

    def shortHelpString(self):
        return "Converts an MAPX document file to a QGS project file."

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFile(
                self.INPUT,
                "Input MAPX file",
                fileFilter="MAPX Documents (*.mapx *.MAPX)",
            )
        )

        super().initAlgorithm(config)

    def autogenerateParameterValues(self, rowParameters, changedParameter, mode):
        if changedParameter == self.INPUT:
            input_file = rowParameters.get(self.INPUT)
            if input_file:
                input_path = Path(input_file)
                if input_path.exists():
                    return {self.OUTPUT: input_path.with_suffix(".qgs").as_posix()}

        return {}

    def processAlgorithm(self, parameters, context, feedback):
        raise QgsProcessingException(
            "This algorithm is available in the licensed version of SLYR only - please see https://north-road.com/slyr/ for details"
        )

    # pylint: enable=missing-docstring,unused-argument
