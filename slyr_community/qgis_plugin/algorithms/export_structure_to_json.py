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
Converts an MXD/LYR document to a JSON representation
"""

from qgis.core import (Qgis,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingException)

from .algorithm import SlyrAlgorithm


class ExportStructureToJson(SlyrAlgorithm):
    """
    Converts an MXD/LYR document to a JSON representation
    """

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'

    # pylint: disable=missing-docstring,unused-argument

    def createInstance(self):
        return ExportStructureToJson()

    def name(self):
        return 'exporttojson'

    def displayName(self):
        return 'Export document structure'

    def shortDescription(self):
        return 'Exports a JSON representation of the internal structure of an MXD (or LYR) document file.'

    def group(self):
        return 'MXD documents'

    def groupId(self):
        return 'mxd'

    def shortHelpString(self):
        return 'This algorithm exports a JSON representation of the internal structure of an ESRI MXD or LYR document file.\n\n' + \
               'It is designed for debugging purposes, allowing users to view in-depth detail about the document structure ' + \
               'and layer configuration.'

    def initAlgorithm(self, config=None):

        if Qgis.QGIS_VERSION_INT >= 31000:
            self.addParameter(QgsProcessingParameterFile(
                self.INPUT, 'Input MXD file',
                fileFilter='ArcGIS Documents (*.mxd, *.MXD, *.lyr, *.LYR);;All files (*.*)'))
        else:
            self.addParameter(QgsProcessingParameterFile(
                self.INPUT, 'Input MXD file', extension='mxd'))

        self.addParameter(QgsProcessingParameterFileDestination(
            self.OUTPUT, 'Destination JSON file', fileFilter='JSON files (*.json *.JSON);;All files (*.*)'))

    def processAlgorithm(self,  # pylint: disable=too-many-locals,too-many-statements
                         parameters,
                         context,
                         feedback):
        raise QgsProcessingException(
            'This algorithm is available in the licensed version of SLYR only - please see https://north-road.com/slyr/ for details')

    # pylint: enable=missing-docstring,unused-argument
