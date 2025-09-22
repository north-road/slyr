"""
Converts all data from the open project to standard formats
"""

# /***************************************************************************
#  *                                                                         *
#  *   This program is free software; you can redistribute it and/or modify  *
#  *   it under the terms of the GNU General Public License as published by  *
#  *   the Free Software Foundation; either version 2 of the License, or     *
#  *   (at your option) any later version.                                   *
#  *                                                                         *
#  ***************************************************************************/

from collections import defaultdict

from qgis.core import (
    QgsProcessingParameterFile,
    QgsProcessingParameterFileDestination,
    QgsProcessingException,
)

from .algorithm import SlyrAlgorithm


class GdbToGpkg(SlyrAlgorithm):
    """
    Converts all data from the open project to standard formats
    """

    INPUT = "INPUT"
    OUTPUT = "OUTPUT"

    def __init__(self):
        super().__init__()
        self.errors = []
        self.converted = defaultdict(list)
        self.converted_count = 0

    # pylint: disable=missing-docstring,unused-argument

    def createInstance(self):
        return GdbToGpkg()

    def name(self):
        return "gdbtogpkg"

    def displayName(self):
        return "Convert File Geodatabase to GeoPackage"

    def shortDescription(self):
        return (
            "Converts all data from an ESRI File Geodatabase to a GeoPackage database"
        )

    def shortHelpString(self):
        return (
            "Converts all data from an ESRI File Geodatabase to a"
            "GeoPackage database.\n\n"
            "This tool will convert:\n\n"
            "<ul><li>All vector layers</li>"
            "<li>Field domains</li>"
            "<li>Field constraints</li>"
            "<li>Field aliases</li>"
            "</ul>"
        )

    def group(self):
        return "Data conversion"

    def groupId(self):
        return "data"

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

    def processAlgorithm(self, parameters, context, feedback):  # pylint: disable=too-many-locals
        raise QgsProcessingException(
            "This algorithm is available in the licensed version of SLYR only - please see https://north-road.com/slyr/ for details"
        )

    # pylint: enable=missing-docstring,unused-argument
