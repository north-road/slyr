"""
Converts annotations in a binary column to a QGIS annotation layer
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
    Qgis,
    QgsProcessingAlgorithm,
    QgsProcessingParameterVectorLayer,
    QgsProcessingParameterField,
    QgsProcessingException,
    QgsProcessingParameterDefinition,
)

from .algorithm import SlyrAlgorithm


class ConvertAnnotations(SlyrAlgorithm):
    """
    Converts annotations in a binary column
    """

    INPUT = "INPUT"
    FIELD = "FIELD"
    OUTPUT = "OUTPUT"

    # pylint: disable=missing-docstring,unused-argument

    def createInstance(self):
        return ConvertAnnotations()

    def name(self):
        return "convertannotations"

    def displayName(self):
        return "Convert annotations"

    def shortDescription(self):
        return ""

    def flags(self):
        return super().flags() | QgsProcessingAlgorithm.Flag.FlagNoThreading

    def group(self):
        return "Annotations"

    def groupId(self):
        return "annotations"

    def shortHelpString(self):
        return ""

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer(self.INPUT, "Input layer"))

        if Qgis.QGIS_VERSION_INT >= 33400:
            field_param = QgsProcessingParameterField(
                self.FIELD,
                "Element field",
                defaultValue="ELEMENT",
                parentLayerParameterName=self.INPUT,
                type=QgsProcessingParameterField.DataType.Binary,
            )
        else:
            field_param = QgsProcessingParameterField(
                self.FIELD,
                "Element field",
                defaultValue="ELEMENT",
                parentLayerParameterName=self.INPUT,
            )
        field_param.setHelp(
            'Select the field containing the ELEMENT data. This is usually the "Element" field, unless a non-standard annotation class structure is in use.'
        )
        field_param.setFlags(
            field_param.flags() | QgsProcessingParameterDefinition.Flag.FlagAdvanced
        )
        self.addParameter(field_param)

    def processAlgorithm(
        self,  # pylint: disable=too-many-locals,too-many-statements,too-many-branches
        parameters,
        context,
        feedback,
    ):
        raise QgsProcessingException(
            "This algorithm is available in the licensed version of SLYR only - please see https://north-road.com/slyr/ for details"
        )

    # pylint: enable=missing-docstring,unused-argument
