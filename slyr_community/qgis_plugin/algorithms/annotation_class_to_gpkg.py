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
SLYR QGIS Processing algorithms
"""

from qgis.core import (QgsProcessingParameterFile,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingException)

from .algorithm import SlyrAlgorithm


class ConvertAnnotationClassToGeopackage(SlyrAlgorithm):
    """
    Converts an annotation class into a standard geopackage
    """

    INPUT = 'INPUT'
    FIELD = 'FIELD'
    OUTPUT = 'OUTPUT'

    # pylint: disable=missing-docstring,unused-argument

    def createInstance(self):
        return ConvertAnnotationClassToGeopackage()

    def name(self):
        return 'convertannotationclasstogpkg'

    def displayName(self):
        return 'Convert annotation classes to GeoPackage (beta)'

    def shortDescription(self):
        return ''

    def group(self):
        return 'Annotations'

    def groupId(self):
        return 'annotations'

    def shortHelpString(self):
        return ''

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFile(
            self.INPUT, 'Input Geodatabase', behavior=QgsProcessingParameterFile.Folder,
            fileFilter='File Geodatabases (*.gdb)'))

        self.addParameter(QgsProcessingParameterFileDestination(
            self.OUTPUT, 'Output GeoPackage', fileFilter='GeoPackage files (*.gpkg)'))

    def processAlgorithm(self,  # pylint: disable=too-many-locals,too-many-statements,too-many-branches
                         parameters,
                         context,
                         feedback):
        raise QgsProcessingException(
            'This algorithm is available in the licensed version of SLYR only - please see https://north-road.com/slyr/ for details')

    # pylint: enable=missing-docstring,unused-argument
