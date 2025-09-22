"""
Converts .lyrx to SLD
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
    Qgis,
    QgsProcessingParameterFile,
    QgsProcessingParameterFileDestination,
    QgsProcessingParameterFolderDestination,
    QgsProcessingParameterString,
    QgsProcessingOutputString,
    QgsProcessingException,
)

from .algorithm import SlyrAlgorithm
from ...converters.context import Context
from ...converters.layers import LayerConverter
from ...parser.exceptions import NotImplementedException, CorruptDocumentException

try:
    from qgis.core import QgsProcessingOutputBoolean  # pylint: disable=ungrouped-imports
except ImportError:
    QgsProcessingOutputBoolean = None


class LyrxToSld(SlyrAlgorithm):
    """
    Converts .lyrx to SLD
    """

    INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    SVG_FOLDER = "SVG_FOLDER"
    SERVER_SVG_PATH = "SERVER_SVG_PATH"
    CONVERTED = "CONVERTED"
    ERROR = "ERROR"

    # pylint: disable=missing-docstring,unused-argument

    def createInstance(self):
        return LyrxToSld()

    def name(self):
        return "lyrxtosld"

    def displayName(self):
        return "Convert LYRX to SLD"

    def shortDescription(self):
        return "Converts an ArcGIS Pro LYRX file to a OGC SLD file"

    def group(self):
        return "SLD"

    def groupId(self):
        return "sld"

    def shortHelpString(self):
        return "Converts an ArcGIS Pro LYRX file to a OGC SLD file"

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFile(self.INPUT, "Input LYRX file", extension="lyrx")
        )

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT, "Destination SLD file", fileFilter="SLD files (*.sld)"
            )
        )

        svg_folder_param = QgsProcessingParameterFolderDestination(
            self.SVG_FOLDER, "Destination folder for SVG files"
        )
        svg_folder_param.setHelp(
            "Local path for storing SVG files generated during the conversion to SLD. These files will all need to be manually copied to the server."
        )
        self.addParameter(svg_folder_param)

        server_svg_path = QgsProcessingParameterString(
            self.SERVER_SVG_PATH, "Server path for SVG files", optional=True
        )
        server_svg_path.setHelp(
            "Path on server where SVG files will be placed. The generated SLDs will contain this path for SVG files. Note that SVGs must be manually copied to this path, this is not handled by the algorithm."
        )
        self.addParameter(server_svg_path)

        if QgsProcessingOutputBoolean is not None:
            self.addOutput(QgsProcessingOutputBoolean(self.CONVERTED, "Converted"))
        self.addOutput(QgsProcessingOutputString(self.ERROR, "Error message"))

    def autogenerateParameterValues(self, rowParameters, changedParameter, mode):
        if changedParameter == self.INPUT:
            input_file = rowParameters.get(self.INPUT)
            if input_file:
                input_path = Path(input_file)
                if input_path.exists():
                    return {self.OUTPUT: input_path.with_suffix(".sld").as_posix()}

        return {}

    def processAlgorithm(
        self,  # pylint: disable=too-many-locals,too-many-statements,too-many-return-statements
        parameters,
        processing_context,
        feedback,
    ):
        raise QgsProcessingException(
            "This algorithm is available in the licensed version of SLYR only - please see https://north-road.com/slyr/ for details"
        )

    # pylint: enable=missing-docstring,unused-argument
