# -*- coding: utf-8 -*-

# /***************************************************************************
# context.py
# ----------
# Date                 : September 2019
# copyright            : (C) 2019 by Nyall Dawson, North Road Consulting
# email                : nyall.dawson@gmail.com
#
#  ***************************************************************************/
#
# /***************************************************************************
#  *                                                                         *
#  *   This program is free software; you can redistribute it and/or modify  *
#  *   it under the terms of the GNU General Public License as published by  *
#  *   the Free Software Foundation; either version 2 of the License, or     *
#  *   (at your option) any later version.                                   *
#  *                                                                         *
#  ***************************************************************************/


"""
Converts an MXD document to a QGS project file, and all data to standard formats
"""

from collections import defaultdict

from qgis.core import QgsProcessingParameterFolderDestination, QgsProcessingException

from .mxd_to_qgs import ConvertMxdToQgs


class ConvertMxdAndData(ConvertMxdToQgs):
    """
    Converts an MXD document to a QGS project file, and all data to standard formats....
    """

    OUTPUT_DATA_FOLDER = "OUTPUT_DATA_FOLDER"

    def __init__(self):
        super().__init__()
        self.errors = []
        self.converted = defaultdict(list)
        self.converted_count = 0

    # pylint: disable=missing-docstring,unused-argument

    def createInstance(self):
        return ConvertMxdAndData()

    def name(self):
        return "convertmxdanddatatoqgs"

    def displayName(self):
        return "Convert MXD/MXT to QGS and data to GPKG (beta)"

    def shortDescription(self):
        return "Converts an MXD or MXT document file to a QGIS project file, and converts all referenced data to standard formats"

    def shortHelpString(self):
        return """Converts an MXD or MXT document file to a QGIS project file, and converts all referenced data to standard formats.\n
        Referenced layer data stored in non-standard formats (such as MDB or GDB files) will be converted to the standard GeoPackage format
        in order to create projects which are optimized for use in QGIS and other open-source tools.
        """

    def initAlgorithm(self, config=None):
        super().initAlgorithm(config)

        self.addParameter(
            QgsProcessingParameterFolderDestination(
                self.OUTPUT_DATA_FOLDER, "Folder to store converted data in"
            )
        )

    def processAlgorithm(self, parameters, context, feedback):  # pylint:disable=too-many-locals,too-many-branches
        raise QgsProcessingException(
            "This algorithm is available in the licensed version of SLYR only - please see https://north-road.com/slyr/ for details"
        )

    # pylint: enable=missing-docstring,unused-argument
