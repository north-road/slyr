"""
Extracts print layouts from an MXD document and adds to the current project
"""

# /***************************************************************************
#  *                                                                         *
#  *   This program is free software; you can redistribute it and/or modify  *
#  *   it under the terms of the GNU General Public License as published by  *
#  *   the Free Software Foundation; either version 2 of the License, or     *
#  *   (at your option) any later version.                                   *
#  *                                                                         *
#  ***************************************************************************/

from qgis.core import QgsProcessingParameterFile

from .algorithm import SlyrAlgorithm


class ExtractPrintLayoutsFromMxd(SlyrAlgorithm):
    """
    Extracts print layouts from an MXD document and adds to the current project
    """

    INPUT = "INPUT"

    # pylint: disable=missing-docstring,unused-argument

    def createInstance(self):
        return ExtractPrintLayoutsFromMxd()

    def name(self):
        return "extractlayoutfrommxd"

    def displayName(self):
        return "Extract print layouts from MXD"

    def shortDescription(self):
        return (
            "Extracts print layouts from an MXD document and "
            "adds them to the current project."
        )

    def group(self):
        return "MXD documents"

    def groupId(self):
        return "mxd"

    def shortHelpString(self):
        return (
            "Extracts print layouts from an MXD document "
            "and adds them to the current project."
        )

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFile(self.INPUT, "Input MXD file", extension="mxd")
        )

    def processAlgorithm(self, parameters, context, feedback):
        return {}

    # pylint: enable=missing-docstring,unused-argument
