"""
QLR to LYRX
"""

from pathlib import Path
import json

from qgis.core import (
    Qgis,
    QgsProcessingParameterFileDestination,
    QgsProcessingException,
    QgsProcessingParameterFile,
    QgsLayerDefinition,
)

from .algorithm import SlyrAlgorithm

from ...converters.context import Context
from ...parser.exceptions import NotImplementedException


class ConvertQlrToLyrx(SlyrAlgorithm):
    """
    Converts a QLR to a LYRX
    """

    INPUT = "INPUT"
    OUTPUT = "OUTPUT"

    # pylint: disable=missing-docstring,unused-argument

    def createInstance(self):
        return ConvertQlrToLyrx()

    def name(self):
        return "qlrtolyrx"

    def displayName(self):
        return "Convert QLR to LYRX"

    def shortDescription(self):
        return "Convert a QGIS QLR file to an ArcGIS Pro LYRX file"

    def group(self):
        return "ArcGIS Pro"

    def groupId(self):
        return "arcgispro"

    def shortHelpString(self):
        return "Converts a QGIS QLR file to an ArcGIS Pro LYRX file."

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFile(
                self.INPUT, "Input QLR file", fileFilter="QLR Files (*.qlr *.QLR)"
            )
        )

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT, "Destination lyrx file", fileFilter="LYRX files (*.lyrx)"
            )
        )

    def autogenerateParameterValues(self, rowParameters, changedParameter, mode):
        if changedParameter == self.INPUT:
            input_file = rowParameters.get(self.INPUT)
            if input_file:
                input_path = Path(input_file)
                if input_path.exists():
                    return {self.OUTPUT: input_path.with_suffix(".lyrx").as_posix()}

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
