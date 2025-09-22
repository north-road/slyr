"""
Converts an QPT document to a PAGX file
"""

import json
from pathlib import Path

from qgis.PyQt.QtCore import QFile, QIODevice
from qgis.PyQt.QtXml import QDomDocument
from qgis.core import (
    Qgis,
    QgsPrintLayout,
    QgsProject,
    QgsProcessingParameterFile,
    QgsProcessingParameterFileDestination,
    QgsReadWriteContext,
    QgsProcessingException,
)

from .algorithm import SlyrAlgorithm
from ...converters.context import Context
from ...converters.layout import LayoutConverter


class ConvertQptToPagx(SlyrAlgorithm):
    """
    Converts an QPT document to a PAGX file
    """

    INPUT = "INPUT"
    OUTPUT = "OUTPUT"

    # pylint: disable=missing-docstring,unused-argument

    def createInstance(self):
        return ConvertQptToPagx()

    def name(self):
        return "convertqpttopagx"

    def displayName(self):
        return "Convert QPT to PAGX (beta)"

    def shortDescription(self):
        return "Converts a QGIS print layout template to a PAGX file."

    def group(self):
        return "ArcGIS Pro"

    def groupId(self):
        return "arcgispro"

    def shortHelpString(self):
        return "Converts a QGIS print layout template to an ArcGIS Pro PAGX file."

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFile(
                self.INPUT, "Input QPT file", fileFilter="QPT Template (*.qpt *.QPT)"
            )
        )

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT, "Destination PAGX file", fileFilter="PAGX files (*.pagx)"
            )
        )

    def autogenerateParameterValues(self, rowParameters, changedParameter, mode):
        if changedParameter == self.INPUT:
            input_file = rowParameters.get(self.INPUT)
            if input_file:
                input_path = Path(input_file)
                if input_path.exists():
                    return {self.OUTPUT: input_path.with_suffix(".pagx").as_posix()}

        return {}

    def processAlgorithm(self, parameters, context, feedback):
        raise QgsProcessingException(
            "This algorithm is available in the licensed version of SLYR only - please see https://north-road.com/slyr/ for details"
        )
