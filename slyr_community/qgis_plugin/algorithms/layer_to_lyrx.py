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

from pathlib import Path
import json

from qgis.core import (
    Qgis,
    QgsProcessingParameterFileDestination,
    QgsProcessingException,
    QgsProcessingParameterMapLayer,
)

from .algorithm import SlyrAlgorithm
from ...parser.exceptions import NotImplementedException


class LayerToLyrx(SlyrAlgorithm):
    """
    Converts a QGIS layer to a LYRX
    """

    INPUT = "INPUT"
    OUTPUT = "OUTPUT"

    # pylint: disable=missing-docstring,unused-argument

    def createInstance(self):
        return LayerToLyrx()

    def name(self):
        return "layertolyrx"

    def displayName(self):
        return "Convert layer to LYRX"

    def shortDescription(self):
        return "Convert a QGIS layer to an ArcGIS Pro LYRX file"

    def group(self):
        return "ArcGIS Pro"

    def groupId(self):
        return "arcgispro"

    def shortHelpString(self):
        return "Converts a QGIS layer to an ArcGIS Pro LYRX file."

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterMapLayer(self.INPUT, "Layer"))

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT, "Destination lyrx file", fileFilter="LYRX files (*.lyrx)"
            )
        )

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
