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
    QgsProcessingAlgorithm,
    QgsProcessingParameterFolderDestination,
)

from .algorithm import SlyrAlgorithm
from qgis.core import QgsProcessingException


class ConvertProjectData(SlyrAlgorithm):
    """
    Converts all data from the open project to standard formats
    """

    OUTPUT_DATA_FOLDER = "OUTPUT_DATA_FOLDER"

    def __init__(self):
        super().__init__()
        self.errors = []
        self.converted = defaultdict(list)
        self.converted_count = 0

    # pylint: disable=missing-docstring,unused-argument

    def createInstance(self):
        return ConvertProjectData()

    def flags(self):
        return super().flags() | QgsProcessingAlgorithm.Flag.FlagNoThreading

    def name(self):
        return "convertprojectdata"

    def displayName(self):
        return "Convert project data to GPKG"

    def shortDescription(self):
        return "Converts all data referenced by the current project to standard formats"

    def shortHelpString(self):
        return (
            "Converts all referenced data from the current project to "
            "standard formats.\n\n"
            "Referenced layer data stored in non-standard formats "
            "(such as MDB or GDB files) will be converted to the "
            "standard GeoPackage format in order to create projects "
            "and data files which are optimized for use in QGIS and "
            "other open-source tools."
        )

    def group(self):
        return "Data conversion"

    def groupId(self):
        return "data"

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFolderDestination(
                self.OUTPUT_DATA_FOLDER, "Folder to store converted data in"
            )
        )

    def processAlgorithm(self, parameters, context, feedback):  # pylint: disable=too-many-locals
        raise QgsProcessingException(
            "This algorithm is available in the licensed version of SLYR only - please see https://north-road.com/slyr/ for details"
        )

    # pylint: enable=missing-docstring,unused-argument
