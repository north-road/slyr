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
Extract hyperlinks from layers to tables algorithm
"""

from qgis.core import (Qgis,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingException)

from .algorithm import SlyrAlgorithm


class ExtractHyperlinksToTables(SlyrAlgorithm):
    """
    Extracts hyperlinks from layers to tables
    """

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'

    # pylint: disable=missing-docstring,unused-argument

    def createInstance(self):
        return ExtractHyperlinksToTables()

    def name(self):
        return 'extracthyperlinks'

    def displayName(self):
        return 'Extract hyperlinks to tables'

    def shortDescription(self):
        return 'Extract hyperlinks from layers to standalone tables'

    def group(self):
        return 'Hyperlinks'

    def groupId(self):
        return 'hyperlinks'

    def shortHelpString(self):
        return 'Extract hyperlinks from layers to standalone tables'

    def initAlgorithm(self, config=None):
        if Qgis.QGIS_VERSION_INT >= 31000:
            self.addParameter(QgsProcessingParameterFile(
                self.INPUT, 'Input MXD/MXT/PMF/LYR file',
                fileFilter='MXD/MXT/PMF/LYR Documents (*.mxd *.MXD *.mxt *.MXT *.pmf *.PMF *.lyr *.LYR)'))
        else:
            self.addParameter(QgsProcessingParameterFile(
                self.INPUT, 'Input MXD/MXT/PMF/LYR file', extension='mxd'))

        self.addParameter(QgsProcessingParameterFileDestination(self.OUTPUT,
                                                                'Destination GeoPackage',
                                                                fileFilter="GPKG files (*.gpkg)"))

    def processAlgorithm(self,  # pylint: disable=too-many-locals,too-many-statements,too-many-branches
                         parameters,
                         context,
                         feedback):
        raise QgsProcessingException(
            'This algorithm is available in the licensed version of SLYR only - please see https://north-road.com/slyr/ for details')

    # pylint: enable=missing-docstring,unused-argument
