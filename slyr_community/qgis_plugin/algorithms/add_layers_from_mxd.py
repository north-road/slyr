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
Adds layers from an MXD document to the current project
"""

from qgis.core import QgsProcessingParameterFile, QgsProcessingException

from .algorithm import SlyrAlgorithm


class AddLayersFromMxd(SlyrAlgorithm):
    """
    Adds layers from an MXD document to the current project
    """

    INPUT = "INPUT"

    def __init__(self):
        super().__init__()
        self.obj = None
        self.input_file = ""

    # pylint: disable=missing-docstring,unused-argument

    def createInstance(self):
        return AddLayersFromMxd()

    def name(self):
        return "addlayersfrommxd"

    def displayName(self):
        return "Add layers from MXD to project"

    def shortDescription(self):
        return "Adds layers from an MXD document to the current project, respecting their original symbology."

    def group(self):
        return "MXD documents"

    def groupId(self):
        return "mxd"

    def shortHelpString(self):
        return "Adds layers from an MXD document to the current project, respecting their original symbology."

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFile(self.INPUT, "Input MXD file", extension="mxd")
        )

    def processAlgorithm(
        self,  # pylint: disable=too-many-locals,too-many-statements
        parameters,
        context,
        feedback,
    ):
        raise QgsProcessingException(
            "This algorithm is available in the licensed version of SLYR only - please see https://north-road.com/slyr/ for details"
        )

    # pylint: enable=missing-docstring,unused-argument
