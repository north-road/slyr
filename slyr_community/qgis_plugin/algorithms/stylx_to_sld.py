"""
Converts .stylx databases to SLD files
"""

# /***************************************************************************
#  *                                                                         *
#  *   This program is free software; you can redistribute it and/or modify  *
#  *   it under the terms of the GNU General Public License as published by  *
#  *   the Free Software Foundation; either version 2 of the License, or     *
#  *   (at your option) any later version.                                   *
#  *                                                                         *
#  ***************************************************************************/

import os
from pathlib import Path

from qgis.PyQt.QtCore import QRegularExpression
from qgis.PyQt.QtXml import QDomDocument
from qgis.core import (
    Qgis,
    QgsProcessingParameterFile,
    QgsSingleSymbolRenderer,
    QgsProcessingParameterEnum,
    QgsProcessingParameterString,
    QgsProcessingOutputNumber,
    QgsProcessingException,
    QgsProcessingParameterFolderDestination,
    QgsProcessingParameterDefinition,
    QgsSymbol,
    QgsVectorLayer,
    QgsFeatureRequest,
)

from .algorithm import SlyrAlgorithm
from ...bintools.extractor import Extractor
from ...converters.context import Context
from ...converters.symbols import SymbolConverter
from ...parser.exceptions import (
    UnreadableSymbolException,
    UnsupportedVersionException,
    NotImplementedException,
    UnknownClsidException,
    UnreadablePictureException,
)


class StylxToSld(SlyrAlgorithm):
    """
    Converts .stylx databases to SLD files
    """

    INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    OBJECT_TYPES = "OBJECT_TYPES"
    FILTER = "FILTER"
    ALL_OBJECT_TYPES = [
        Extractor.FILL_SYMBOLS,
        Extractor.LINE_SYMBOLS,
        Extractor.MARKER_SYMBOLS,
    ]

    MARKER_SYMBOL_COUNT = "MARKER_SYMBOL_COUNT"
    LINE_SYMBOL_COUNT = "LINE_SYMBOL_COUNT"
    FILL_SYMBOL_COUNT = "FILL_SYMBOL_COUNT"
    UNREADABLE_MARKER_SYMBOLS = "UNREADABLE_MARKER_SYMBOLS"
    UNREADABLE_LINE_SYMBOLS = "UNREADABLE_LINE_SYMBOLS"
    UNREADABLE_FILL_SYMBOLS = "UNREADABLE_FILL_SYMBOLS"
    SVG_FOLDER = "SVG_FOLDER"
    SERVER_SVG_PATH = "SERVER_SVG_PATH"

    # pylint: disable=missing-docstring,unused-argument

    def createInstance(self):
        return StylxToSld()

    def name(self):
        return "stylxtosld"

    def displayName(self):
        return "Convert STYLX to SLD"

    def shortDescription(self):
        return "Converts an ESRI stylx database to a OGC SLD file (or files)"

    def group(self):
        return "SLD"

    def groupId(self):
        return "sld"

    def shortHelpString(self):
        return (
            "Converts an ESRI stylx database to an OGC SLD file. "
            "Each symbol in the stylx database will be "
            "converted to an individual OGC SLD file."
        )

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFile(self.INPUT, "Stylx database", extension="stylx")
        )

        type_filter = QgsProcessingParameterEnum(
            self.OBJECT_TYPES,
            "Objects to extract",
            [Extractor.OBJECT_TYPE_NAMES[t] for t in self.ALL_OBJECT_TYPES],
            allowMultiple=True,
            defaultValue=list(range(len(self.ALL_OBJECT_TYPES))),
            optional=True,
        )
        type_filter.setFlags(
            type_filter.flags() | QgsProcessingParameterDefinition.Flag.FlagAdvanced
        )
        self.addParameter(type_filter)

        self.addParameter(
            QgsProcessingParameterFolderDestination(
                self.OUTPUT, "Destination folder for SLDs"
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

        filter_param = QgsProcessingParameterString(
            self.FILTER, "Filter items by name", optional=True
        )
        filter_param.setFlags(
            filter_param.flags() | QgsProcessingParameterDefinition.Flag.FlagAdvanced
        )
        self.addParameter(filter_param)

        self.addOutput(
            QgsProcessingOutputNumber(self.FILL_SYMBOL_COUNT, "Fill Symbol Count")
        )
        self.addOutput(
            QgsProcessingOutputNumber(self.LINE_SYMBOL_COUNT, "Line Symbol Count")
        )
        self.addOutput(
            QgsProcessingOutputNumber(self.MARKER_SYMBOL_COUNT, "Marker Symbol Count")
        )
        self.addOutput(
            QgsProcessingOutputNumber(
                self.UNREADABLE_FILL_SYMBOLS, "Unreadable Fill Symbol Count"
            )
        )
        self.addOutput(
            QgsProcessingOutputNumber(
                self.UNREADABLE_LINE_SYMBOLS, "Unreadable Line Symbol Count"
            )
        )
        self.addOutput(
            QgsProcessingOutputNumber(
                self.UNREADABLE_MARKER_SYMBOLS, "Unreadable Marker Symbol Count"
            )
        )

    def autogenerateParameterValues(self, rowParameters, changedParameter, mode):
        if changedParameter == self.INPUT:
            input_file = rowParameters.get(self.INPUT)
            if input_file:
                input_path = Path(input_file)
                if input_path.exists():
                    return {self.OUTPUT: input_path.with_suffix(".sld").as_posix()}

        return {}

    def processAlgorithm(
        self,  # pylint:disable=too-many-locals,too-many-statements,too-many-branches
        parameters,
        context,
        feedback,
    ):
        raise QgsProcessingException(
            "This algorithm is available in the licensed version of SLYR only - please see https://north-road.com/slyr/ for details"
        )

    # pylint: enable=missing-docstring,unused-argument
