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

from typing import Optional

from qgis.core import (
    QgsProcessingParameterFile,
    QgsProcessingOutputString,
    QgsProcessingException,
)


from .algorithm import SlyrAlgorithm


class ConvertPagxToQgs(SlyrAlgorithm):
    """
    Converts an PAGX document to a QGS project layout file
    """

    INPUT = "INPUT"
    LAYOUT_NAME = "LAYOUT_NAME"

    # pylint: disable=missing-docstring,unused-argument

    def __init__(self):
        super().__init__()
        self.input_file: Optional[str] = None

    def createInstance(self):
        return ConvertPagxToQgs()

    def name(self):
        return "convertpagxtoqgs"

    def displayName(self):
        return "Import PAGX print layout"

    def shortDescription(self):
        return "Imports a PAGX print layout into the current QGIS project."

    def group(self):
        return "ArcGIS Pro"

    def groupId(self):
        return "arcgispro"

    def shortHelpString(self):
        return "Imports a PAGX print layout into the current QGIS project."

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFile(
                self.INPUT,
                "Input PAGX file",
                fileFilter="PAGX Documents (*.pagx *.PAGX)",
            )
        )

        self.addOutput(QgsProcessingOutputString(self.LAYOUT_NAME, "Layout name"))

    def processAlgorithm(self, parameters, context, feedback):
        raise QgsProcessingException(
            "This algorithm is available in the licensed version of SLYR only - please see https://north-road.com/slyr/ for details"
        )
