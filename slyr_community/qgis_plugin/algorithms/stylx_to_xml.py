"""
Converts .stylx databases to QGIS Style XML databases
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

from qgis.PyQt.QtCore import QVariant, QRegularExpression
from qgis.core import (
    Qgis,
    QgsProcessing,
    QgsProcessingParameterFile,
    QgsProcessingParameterFileDestination,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterEnum,
    QgsProcessingParameterString,
    QgsProcessingOutputNumber,
    QgsProcessingException,
    QgsProcessingParameterDefinition,
    QgsStyle,
    QgsFeature,
    QgsFields,
    QgsField,
    QgsColorRamp,
    QgsSymbol,
    QgsTextFormat,
    QgsPalLayerSettings,
    QgsVectorLayer,
    QgsFeatureRequest,
    QgsWkbTypes,
)

from .algorithm import SlyrAlgorithm
from ...bintools.extractor import Extractor
from ...converters.color_ramp import ColorRampConverter
from ...converters.context import Context
from ...converters.labels import LabelConverter
from ...converters.symbols import SymbolConverter

from ...parser.exceptions import (
    UnreadableSymbolException,
    UnsupportedVersionException,
    NotImplementedException,
    UnknownClsidException,
    UnreadablePictureException,
)


class StylxToQgisXml(SlyrAlgorithm):
    """
    Converts .stylx databases to QGIS Style XML databases
    """

    INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    REPORT = "REPORT"
    OBJECT_TYPES = "OBJECT_TYPES"
    FILTER = "FILTER"
    ALL_OBJECT_TYPES = [
        Extractor.FILL_SYMBOLS,
        Extractor.LINE_SYMBOLS,
        Extractor.MARKER_SYMBOLS,
        Extractor.COLOR_RAMPS,
        Extractor.TEXT_SYMBOLS,
        Extractor.LABELS,
    ]

    MARKER_SYMBOL_COUNT = "MARKER_SYMBOL_COUNT"
    LINE_SYMBOL_COUNT = "LINE_SYMBOL_COUNT"
    FILL_SYMBOL_COUNT = "FILL_SYMBOL_COUNT"
    COLOR_RAMP_COUNT = "COLOR_RAMP_COUNT"
    TEXT_FORMAT_COUNT = "TEXT_FORMAT_COUNT"
    LABEL_SETTINGS_COUNT = "LABEL_SETTINGS_COUNT"
    UNREADABLE_MARKER_SYMBOLS = "UNREADABLE_MARKER_SYMBOLS"
    UNREADABLE_LINE_SYMBOLS = "UNREADABLE_LINE_SYMBOLS"
    UNREADABLE_FILL_SYMBOLS = "UNREADABLE_FILL_SYMBOLS"
    UNREADABLE_COLOR_RAMPS = "UNREADABLE_COLOR_RAMPS"
    UNREADABLE_TEXT_FORMATS = "UNREADABLE_TEXT_FORMATS"
    UNREADABLE_LABEL_SETTINGS = "UNREADABLE_LABEL_SETTINGS"

    # pylint: disable=missing-docstring,unused-argument

    def createInstance(self):
        return StylxToQgisXml()

    def name(self):
        return "stylxtoqgisxml"

    def displayName(self):
        return "Convert STYLX to QGIS style XML"

    def shortDescription(self):
        return "Converts an ArcGIS Pro STYLX database to a QGIS XML Style library"

    def group(self):
        return "ArcGIS Pro"

    def groupId(self):
        return "arcgispro"

    def shortHelpString(self):
        return "Converts an ArcGIS Pro STYLX database to a QGIS XML Style library"

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
            QgsProcessingParameterFileDestination(
                self.OUTPUT, "Destination XML file", fileFilter="XML files (*.xml)"
            )
        )

        filter_param = QgsProcessingParameterString(
            self.FILTER, "Filter items by name", optional=True
        )
        filter_param.setFlags(
            filter_param.flags() | QgsProcessingParameterDefinition.Flag.FlagAdvanced
        )
        self.addParameter(filter_param)

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.REPORT,
                "Unconvertable symbols report",
                QgsProcessing.SourceType.TypeVector,
                None,
                True,
                False,
            )
        )

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
            QgsProcessingOutputNumber(self.COLOR_RAMP_COUNT, "Color Ramp Count")
        )
        self.addOutput(
            QgsProcessingOutputNumber(self.TEXT_FORMAT_COUNT, "Text Format Count")
        )
        self.addOutput(
            QgsProcessingOutputNumber(self.LABEL_SETTINGS_COUNT, "Label Settings Count")
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
        self.addOutput(
            QgsProcessingOutputNumber(
                self.UNREADABLE_COLOR_RAMPS, "Unreadable Color Ramps"
            )
        )
        self.addOutput(
            QgsProcessingOutputNumber(
                self.UNREADABLE_TEXT_FORMATS, "Unreadable Text Formats"
            )
        )
        self.addOutput(
            QgsProcessingOutputNumber(
                self.UNREADABLE_LABEL_SETTINGS, "Unreadable Label Settings"
            )
        )

    def autogenerateParameterValues(self, rowParameters, changedParameter, mode):
        if changedParameter == self.INPUT:
            input_file = rowParameters.get(self.INPUT)
            if input_file:
                input_path = Path(input_file)
                if input_path.exists():
                    return {self.OUTPUT: input_path.with_suffix(".xml").as_posix()}

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
