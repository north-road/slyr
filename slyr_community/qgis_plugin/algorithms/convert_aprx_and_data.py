"""
Converts an APRX document to a QGS project file, and all data to standard formats
"""

# /***************************************************************************
#  *                                                                         *
#  *   This program is free software; you can redistribute it and/or modify  *
#  *   it under the terms of the GNU General Public License as published by  *
#  *   the Free Software Foundation; either version 2 of the License, or     *
#  *   (at your option) any later version.                                   *
#  *                                                                         *
#  ***************************************************************************/

import pathlib

from qgis.core import (
    QgsProcessingParameterFolderDestination,
    QgsProcessingException,
    QgsProcessingParameterFile,
)

from .arcpro_to_qgs import ConvertArcProToQgs
from .utils import AlgorithmUtils


class ConvertAprxAndData(ConvertArcProToQgs):
    """
    Converts an APRX document to a QGS project file, and all data to standard formats....
    """

    OUTPUT_DATA_FOLDER = "OUTPUT_DATA_FOLDER"

    # pylint: disable=missing-docstring,unused-argument

    def createInstance(self):
        return ConvertAprxAndData()

    def name(self):
        return "convertaprxanddatatoqgs"

    def displayName(self):
        return "Convert APRX/MAPX to QGS and data to GPKG"

    def shortDescription(self):
        return (
            "Converts an APRX or MAPX document file to a QGIS project "
            "file, and converts all referenced data to standard formats"
        )

    def shortHelpString(self):
        return (
            "Converts an APRX or MAPX document file to a QGIS project "
            "file, and converts all referenced data to standard formats.\n\n"
            "Referenced layer data stored in non-standard formats (such "
            "as MDB or GDB files) will be converted to the standard "
            "GeoPackage format in order to create projects which are "
            "optimized for use in QGIS and other open-source tools."
        )

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFile(
                self.INPUT,
                "Input APRX/MAPX file",
                fileFilter="ArcGIS Pro Documents (*.aprx *.APRX *.mapx *.MAPX);;APRX Documents (*.aprx *.APRX);;MAPX Documents (*.mapx *.MAPX)",
            )
        )

        super().initAlgorithm(config)

        self.addParameter(
            QgsProcessingParameterFolderDestination(
                self.OUTPUT_DATA_FOLDER, "Folder to store converted data in"
            )
        )

    def autogenerateParameterValues(self, rowParameters, changedParameter, mode):
        if changedParameter == self.INPUT:
            input_file = rowParameters.get(self.INPUT)
            if input_file:
                input_path = pathlib.Path(input_file)
                if input_path.exists():
                    return {self.OUTPUT: input_path.with_suffix(".qgs").as_posix()}

        return {}

    def processAlgorithm(self, parameters, context, feedback):  # pylint:disable=too-many-locals,too-many-branches
        raise QgsProcessingException(
            "This algorithm is available in the licensed version of SLYR only - please see https://north-road.com/slyr/ for details"
        )

    # pylint: enable=missing-docstring,unused-argument
