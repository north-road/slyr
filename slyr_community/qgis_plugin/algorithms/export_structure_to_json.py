"""
Converts an MXD/LYR document to a JSON representation
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
import os
from pathlib import Path

from qgis.core import (
    QgsProcessingParameterFile,
    QgsProcessingParameterFileDestination,
    QgsProcessingException,
)

from .algorithm import SlyrAlgorithm
from .utils import AlgorithmUtils
from ...converters.context import Context
from ...parser.exceptions import (
    UnreadableSymbolException,
    NotImplementedException,
    UnknownClsidException,
    EmptyDocumentException,
    DocumentTypeException,
)
from ...parser.streams.layer import LayerFile
from ...parser.streams.map_document import MapDocument


class ExportStructureToJson(SlyrAlgorithm):
    """
    Converts an MXD/LYR document to a JSON representation
    """

    INPUT = "INPUT"
    OUTPUT = "OUTPUT"

    # pylint: disable=missing-docstring,unused-argument

    def createInstance(self):
        return ExportStructureToJson()

    def name(self):
        return "exporttojson"

    def displayName(self):
        return "Export document structure"

    def shortDescription(self):
        return (
            "Exports a JSON representation of the internal structure of "
            "an MXD (or LYR) document file."
        )

    def group(self):
        return "MXD documents"

    def groupId(self):
        return "mxd"

    def shortHelpString(self):
        return (
            "This algorithm exports a JSON representation of the internal "
            "structure of an ESRI MXD or LYR document file.\n\n"
            "It is designed for debugging purposes, allowing users to "
            "view in-depth detail about the document structure "
            "and layer configuration."
        )

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFile(
                self.INPUT,
                "Input MXD file",
                fileFilter="ArcGIS Documents (*.mxd, *.MXD, *.lyr, *.LYR);;All files (*.*)",
            )
        )

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT,
                "Destination JSON file",
                fileFilter="JSON files (*.json *.JSON);;All files (*.*)",
            )
        )

    def autogenerateParameterValues(self, rowParameters, changedParameter, mode):
        if changedParameter == self.INPUT:
            input_file = rowParameters.get(self.INPUT)
            if input_file:
                input_path = Path(input_file)
                if input_path.exists():
                    return {self.OUTPUT: input_path.with_suffix(".json").as_posix()}

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
