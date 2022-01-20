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
Converts .avl to QML
"""

from qgis.core import (QgsProcessingParameterFile,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingOutputString,
                       QgsProcessingException)

from .algorithm import SlyrAlgorithm

HAS_BOOLEAN_OUTPUT = False
try:
    from qgis.core import QgsProcessingOutputBoolean  # pylint: disable=ungrouped-imports

    HAS_BOOLEAN_OUTPUT = True
except ImportError:
    QgsProcessingOutputBoolean = None


class AvlToQml(SlyrAlgorithm):
    """
    Converts .avl to QML
    """

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    CONVERTED = 'CONVERTED'
    ERROR = 'ERROR'

    # pylint: disable=missing-docstring,unused-argument

    def createInstance(self):
        return AvlToQml()

    def name(self):
        return 'avltoqml'

    def displayName(self):
        return 'Convert AVL to QML'

    def shortDescription(self):
        return 'Converts an ESRI ArcInfo AVL file to a QGIS QML file'

    def group(self):
        return 'AVL styles'

    def groupId(self):
        return 'avl'

    def shortHelpString(self):
        return "Converts an ESRI ArcInfo AVL file to a QGIS QML file."

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFile(
            self.INPUT, 'Input AVL file', extension='avl'))

        self.addParameter(QgsProcessingParameterFileDestination(
            self.OUTPUT, 'Destination QML file', fileFilter='QML files (*.qml)'))

        if HAS_BOOLEAN_OUTPUT:
            self.addOutput(QgsProcessingOutputBoolean(self.CONVERTED, 'Converted'))
        self.addOutput(QgsProcessingOutputString(self.ERROR, 'Error message'))

    def processAlgorithm(self,  # pylint: disable=too-many-locals,too-many-statements
                         parameters,
                         context,
                         feedback):
        raise QgsProcessingException(
            'This algorithm is available in the licensed version of SLYR only - please see https://north-road.com/slyr/ for details')

    # pylint: enable=missing-docstring,unused-argument
