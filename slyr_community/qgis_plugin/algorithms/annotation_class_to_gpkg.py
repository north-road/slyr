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

import base64
import json
import os
import struct
from io import BytesIO
from json import JSONDecodeError
from pathlib import Path

from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtGui import QFont
from qgis.PyQt.QtXml import QDomDocument
from qgis.core import (
    Qgis,
    QgsProcessingParameterFile,
    QgsProcessingParameterFileDestination,
    QgsProcessingException,
    QgsFeature,
    QgsFields,
    QgsField,
    QgsWkbTypes,
    QgsProject,
    QgsProviderRegistry,
    QgsVectorLayer,
    QgsProcessingMultiStepFeedback,
    QgsFeatureSink,
    QgsFeatureRequest,
    QgsProcessingUtils,
    NULL,
    QgsProcessingContext,
    QgsGeometry,
    QgsPoint,
)

from .algorithm import SlyrAlgorithm
from ...converters.context import Context
from ...converters.geometry import GeometryConverter
from ...converters.text_format import TextSymbolConverter
from ...converters.annotations import AnnotationConverter
from ...parser.exceptions import (
    UnreadableSymbolException,
    NotImplementedException,
    EmptyDocumentException,
    UnknownClsidException,
)
from ...parser.stream import Stream
from .utils import AlgorithmUtils


class ConvertAnnotationClassToGeopackage(SlyrAlgorithm):
    """
    Converts an annotation class into a standard geopackage
    """

    INPUT = "INPUT"
    FIELD = "FIELD"
    OUTPUT = "OUTPUT"

    # pylint: disable=missing-docstring,unused-argument

    def createInstance(self):
        return ConvertAnnotationClassToGeopackage()

    def name(self):
        return "convertannotationclasstogpkg"

    def displayName(self):
        return "Convert annotation classes to GeoPackage"

    def shortDescription(self):
        return ""

    def group(self):
        return "Annotations"

    def groupId(self):
        return "annotations"

    def shortHelpString(self):
        return ""

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFile(
                self.INPUT,
                "Input Geodatabase",
                behavior=QgsProcessingParameterFile.Behavior.Folder,
                fileFilter="File Geodatabases (*.gdb)",
            )
        )

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT, "Output GeoPackage", fileFilter="GeoPackage files (*.gpkg)"
            )
        )

    def processAlgorithm(
        self,  # pylint: disable=too-many-locals,too-many-statements,too-many-branches
        parameters,
        context,
        feedback,
    ):
        raise QgsProcessingException(
            "This algorithm is available in the licensed version of SLYR only - please see https://north-road.com/slyr/ for details"
        )

    # pylint: enable=missing-docstring,unused-argument
