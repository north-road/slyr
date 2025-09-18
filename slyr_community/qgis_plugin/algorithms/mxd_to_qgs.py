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
Converts an MXD document to a QGS project file
"""

from qgis.core import (
    Qgis,
    QgsProcessingParameterFile,
    QgsProcessingParameterFileDestination,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterDefinition,
    QgsProcessingException,
)

from .algorithm import SlyrAlgorithm


class ConvertMxdToQgs(SlyrAlgorithm):
    """
    Converts an MXD document to a QGS project file
    """

    INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    IGNORE_ONLINE = "IGNORE_ONLINE"

    # pylint: disable=missing-docstring,unused-argument

    def createInstance(self):
        return ConvertMxdToQgs()

    def name(self):
        return "convertmxdtoqgs"

    def displayName(self):
        return "Convert MXD/MXT to QGS"

    def shortDescription(self):
        return "Converts an MXD or MXT document file to a QGIS project file."

    def group(self):
        return "MXD documents"

    def groupId(self):
        return "mxd"

    def shortHelpString(self):
        return "Converts an MXD or MXT document file to a QGIS project file."

    def initAlgorithm(self, config=None):
        if Qgis.QGIS_VERSION_INT >= 31000:
            self.addParameter(
                QgsProcessingParameterFile(
                    self.INPUT,
                    "Input MXD/MXT file",
                    fileFilter="MXD/MXT Documents (*.mxd *.MXD *.mxt *.MXT)",
                )
            )
        else:
            self.addParameter(
                QgsProcessingParameterFile(
                    self.INPUT, "Input MXD/MXT file", extension="mxd"
                )
            )

        param_no_online = QgsProcessingParameterBoolean(
            self.IGNORE_ONLINE, "Ignore online sources (debug option)", False, True
        )
        param_no_online.setFlags(
            param_no_online.flags() | QgsProcessingParameterDefinition.FlagHidden
        )
        self.addParameter(param_no_online)

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT,
                "Destination QGS project file",
                fileFilter="QGS files (*.qgs)",
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        raise QgsProcessingException(
            "This algorithm is available in the licensed version of SLYR only - please see https://north-road.com/slyr/ for details"
        )

    # pylint: enable=missing-docstring,unused-argument
