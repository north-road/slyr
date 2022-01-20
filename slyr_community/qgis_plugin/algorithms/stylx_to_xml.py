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
Converts .stylx databases to QGIS Style XML databases
"""

from qgis.core import (QgsProcessing,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingOutputNumber,
                       QgsProcessingException)

from .algorithm import SlyrAlgorithm


class StylxToQgisXml(SlyrAlgorithm):
    """
    Converts .stylx databases to QGIS Style XML databases
    """

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    REPORT = 'REPORT'

    MARKER_SYMBOL_COUNT = 'MARKER_SYMBOL_COUNT'
    LINE_SYMBOL_COUNT = 'LINE_SYMBOL_COUNT'
    FILL_SYMBOL_COUNT = 'FILL_SYMBOL_COUNT'
    COLOR_RAMP_COUNT = 'COLOR_RAMP_COUNT'
    TEXT_FORMAT_COUNT = 'TEXT_FORMAT_COUNT'
    LABEL_SETTINGS_COUNT = 'LABEL_SETTINGS_COUNT'
    LINE_PATCH_COUNT = 'LINE_PATCH_COUNT'
    AREA_PATCH_COUNT = 'AREA_PATCH_COUNT'
    UNREADABLE_MARKER_SYMBOLS = 'UNREADABLE_MARKER_SYMBOLS'
    UNREADABLE_LINE_SYMBOLS = 'UNREADABLE_LINE_SYMBOLS'
    UNREADABLE_FILL_SYMBOLS = 'UNREADABLE_FILL_SYMBOLS'
    UNREADABLE_COLOR_RAMPS = 'UNREADABLE_COLOR_RAMPS'
    UNREADABLE_TEXT_FORMATS = 'UNREADABLE_TEXT_FORMATS'
    UNREADABLE_LABEL_SETTINGS = 'UNREADABLE_LABEL_SETTINGS'
    UNREADABLE_LINE_PATCHES = 'UNREADABLE_LINE_PATCHES'
    UNREADABLE_AREA_PATCHES = 'UNREADABLE_AREA_PATCHES'

    # pylint: disable=missing-docstring,unused-argument

    def createInstance(self):
        return StylxToQgisXml()

    def name(self):
        return 'stylxtoqgisxml'

    def displayName(self):
        return 'Convert stylx to QGIS style XML'

    def shortDescription(self):
        return 'Converts an ArcGIS Pro stylx database to a QGIS XML Style library'

    def group(self):
        return 'ArcGIS Pro'

    def groupId(self):
        return 'arcgispro'

    def shortHelpString(self):
        return "Converts an ArcGIS Pro stylx database to a QGIS XML Style library"

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFile(
            self.INPUT, 'Stylx database', extension='stylx'))

        self.addParameter(QgsProcessingParameterFileDestination(self.OUTPUT,
                                                                'Destination XML file', fileFilter="XML files (*.xml)"))

        self.addParameter(QgsProcessingParameterFeatureSink(self.REPORT, 'Unconvertable symbols report',
                                                            QgsProcessing.TypeVector, None, True, False))

        self.addOutput(QgsProcessingOutputNumber(self.FILL_SYMBOL_COUNT, 'Fill Symbol Count'))
        self.addOutput(QgsProcessingOutputNumber(self.LINE_SYMBOL_COUNT, 'Line Symbol Count'))
        self.addOutput(QgsProcessingOutputNumber(self.MARKER_SYMBOL_COUNT, 'Marker Symbol Count'))
        self.addOutput(QgsProcessingOutputNumber(self.COLOR_RAMP_COUNT, 'Color Ramp Count'))
        self.addOutput(QgsProcessingOutputNumber(self.TEXT_FORMAT_COUNT, 'Text Format Count'))
        self.addOutput(QgsProcessingOutputNumber(self.LINE_PATCH_COUNT, 'Line Patch Count'))
        self.addOutput(QgsProcessingOutputNumber(self.AREA_PATCH_COUNT, 'Area Patch Count'))
        self.addOutput(QgsProcessingOutputNumber(self.UNREADABLE_FILL_SYMBOLS, 'Unreadable Fill Symbol Count'))
        self.addOutput(QgsProcessingOutputNumber(self.UNREADABLE_LINE_SYMBOLS, 'Unreadable Line Symbol Count'))
        self.addOutput(QgsProcessingOutputNumber(self.UNREADABLE_MARKER_SYMBOLS, 'Unreadable Marker Symbol Count'))
        self.addOutput(QgsProcessingOutputNumber(self.UNREADABLE_COLOR_RAMPS, 'Unreadable Color Ramps'))
        self.addOutput(QgsProcessingOutputNumber(self.UNREADABLE_TEXT_FORMATS, 'Unreadable Text Formats'))
        self.addOutput(QgsProcessingOutputNumber(self.UNREADABLE_LINE_PATCHES, 'Unreadable Line Patches'))
        self.addOutput(QgsProcessingOutputNumber(self.UNREADABLE_AREA_PATCHES, 'Unreadable Area Patches'))

    def processAlgorithm(self,  # pylint:disable=too-many-locals,too-many-statements,too-many-branches
                         parameters,
                         context,
                         feedback):
        raise QgsProcessingException(
            'This algorithm is available in the licensed version of SLYR only - please see https://north-road.com/slyr/ for details')

    # pylint: enable=missing-docstring,unused-argument
