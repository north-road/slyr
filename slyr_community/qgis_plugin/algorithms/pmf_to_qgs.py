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
Converts a PMF document to a QGS project file
"""

from qgis.core import (QgsProcessingParameterFile,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingException)

from .algorithm import SlyrAlgorithm


class ConvertPmfToQgs(SlyrAlgorithm):
    """
    Converts a PMF document to a QGS project file
    """

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'

    # pylint: disable=missing-docstring,unused-argument

    def createInstance(self):
        return ConvertPmfToQgs()

    def name(self):
        return 'convertpmftoqgs'

    def displayName(self):
        return 'Convert PMF to QGS'

    def shortDescription(self):
        return 'Converts a PMF document file to a QGIS project file.'

    def group(self):
        return 'PMF published maps'

    def groupId(self):
        return 'pmf'

    def shortHelpString(self):
        return 'Converts a PMF document file to a QGIS project file.'

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFile(
            self.INPUT, 'Input PMF file', extension='pmf'))

        self.addParameter(QgsProcessingParameterFileDestination(
            self.OUTPUT, 'Destination QGS project file', fileFilter='QGS files (*.qgs)'))

    def processAlgorithm(self,  # pylint: disable=too-many-locals,too-many-statements
                         parameters,
                         context,
                         feedback):
        raise QgsProcessingException(
            'This algorithm is available in the licensed version of SLYR only - please see https://north-road.com/slyr/ for details')

    # pylint: enable=missing-docstring,unused-argument
