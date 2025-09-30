"""
Converts an APRX document to a QGS project file
"""

# /***************************************************************************
#  *                                                                         *
#  *   This program is free software; you can redistribute it and/or modify  *
#  *   it under the terms of the GNU General Public License as published by  *
#  *   the Free Software Foundation; either version 2 of the License, or     *
#  *   (at your option) any later version.                                   *
#  *                                                                         *
#  ***************************************************************************/

from qgis.core import (
    QgsProcessingParameterFileDestination,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterDefinition,
)

from .algorithm import SlyrAlgorithm


class ConvertArcProToQgs(SlyrAlgorithm):
    """
    Converts an ArcGIS Pro document to a QGS project file
    """

    INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    TEST_MODE = "TEST_MODE"

    # pylint: disable=missing-docstring,unused-argument

    def group(self):
        return "ArcGIS Pro"

    def groupId(self):
        return "arcgispro"

    def initAlgorithm(self, config=None):
        param_test_mode = QgsProcessingParameterBoolean(
            self.TEST_MODE, "Test mode (debug option)", False, True
        )
        param_test_mode.setFlags(
            param_test_mode.flags() | QgsProcessingParameterDefinition.Flag.FlagHidden
        )
        self.addParameter(param_test_mode)

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT,
                "Destination QGS project file",
                fileFilter="QGS files (*.qgs);;QGZ files (*.qgz)",
            )
        )

    # pylint: enable=missing-docstring,unused-argument

    @staticmethod
    def convert_aprx(input_file, feedback, test_mode: bool, context):
        """
        Converts an APRX project
        """

    @staticmethod
    def convert_mapx(input_file, feedback, test_mode: bool, context):
        """
        Converts an MAPX project
        """
