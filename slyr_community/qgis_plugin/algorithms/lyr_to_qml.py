"""
Converts .lyr to QML
"""

# /***************************************************************************
#  *                                                                         *
#  *   This program is free software; you can redistribute it and/or modify  *
#  *   it under the terms of the GNU General Public License as published by  *
#  *   the Free Software Foundation; either version 2 of the License, or     *
#  *   (at your option) any later version.                                   *
#  *                                                                         *
#  ***************************************************************************/

from pathlib import Path

from qgis.core import (
    Qgis,
    QgsProcessingParameterFile,
    QgsProcessingParameterFileDestination,
    QgsProcessingOutputString,
)

from .algorithm import SlyrAlgorithm
from ...converters.context import Context
from ...converters.layers import LayerConverter
from ...parser.exceptions import (
    UnreadableSymbolException,
    NotImplementedException,
    UnknownClsidException,
)
from ...parser.objects.group_layer import GroupLayer
from ...parser.stream import Stream
from qgis.core import QgsProcessingException
from ...parser.exceptions import RequiresLicenseException

try:
    from qgis.core import QgsProcessingOutputBoolean  # pylint: disable=ungrouped-imports
except ImportError:
    QgsProcessingOutputBoolean = None


class LyrToQml(SlyrAlgorithm):
    """
    Converts .lyr to QML
    """

    INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    CONVERTED = "CONVERTED"
    ERROR = "ERROR"

    # pylint: disable=missing-docstring,unused-argument

    def createInstance(self):
        return LyrToQml()

    def name(self):
        return "lyrtoqml"

    def displayName(self):
        return "Convert LYR to QML"

    def shortDescription(self):
        return "Converts an ESRI LYR file to a QGIS QML file (or files)"

    def group(self):
        return "LYR datasets"

    def groupId(self):
        return "lyr"

    def shortHelpString(self):
        return (
            "Converts an ESRI LYR file to a QGIS QML file. If multiple "
            "layers are present in the LYR file, each will be "
            "converted to an individual QML file."
        )

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFile(self.INPUT, "Input LYR file", extension="lyr")
        )

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT, "Destination QML file", fileFilter="QML files (*.qml)"
            )
        )

        if QgsProcessingOutputBoolean is not None:
            self.addOutput(QgsProcessingOutputBoolean(self.CONVERTED, "Converted"))
        self.addOutput(QgsProcessingOutputString(self.ERROR, "Error message"))

    def autogenerateParameterValues(self, rowParameters, changedParameter, mode):
        if changedParameter == self.INPUT:
            input_file = rowParameters.get(self.INPUT)
            if input_file:
                input_path = Path(input_file)
                if input_path.exists():
                    return {self.OUTPUT: input_path.with_suffix(".qml").as_posix()}

        return {}

    def processAlgorithm(
        self,  # pylint: disable=too-many-locals,too-many-statements,too-many-return-statements
        parameters,
        context,
        feedback,
    ):
        input_file = self.parameterAsString(parameters, self.INPUT, context)
        output_file = self.parameterAsFileOutput(parameters, self.OUTPUT, context)

        warnings = set()
        info = set()
        with open(input_file, "rb") as f:
            stream = Stream(f, False, force_layer=True, offset=0)
            try:
                obj = stream.read_object()
            except UnknownClsidException as e:
                feedback.reportError(str(e), fatalError=True)
                return {self.ERROR: str(e), self.CONVERTED: False, self.OUTPUT: None}
            except RequiresLicenseException as e:
                raise QgsProcessingException(
                    "{} - please see https://north-road.com/slyr/ for details".format(e)
                ) from e
            except UnreadableSymbolException as e:
                err = "Unreadable object: {}".format(e)
                feedback.reportError(err, fatalError=True)
                return {self.ERROR: err, self.CONVERTED: False, self.OUTPUT: None}
            except NotImplementedException as e:
                feedback.reportError(str(e), fatalError=True)
                return {self.ERROR: str(e), self.CONVERTED: False, self.OUTPUT: None}
            except UnicodeDecodeError as e:
                err = "Unreadable object: {}".format(e)
                feedback.reportError(err, fatalError=True)
                return {self.ERROR: err, self.CONVERTED: False, self.OUTPUT: None}

        if not LayerConverter.is_layer(obj) and not isinstance(obj, GroupLayer):
            err = "Objects of type {} are not supported".format(obj.__class__.__name__)
            feedback.reportError(err, fatalError=False)
            return {self.ERROR: err, self.CONVERTED: False, self.OUTPUT: None}

        def on_error(error):
            feedback.reportError(error, fatalError=False)

        def unsupported_object_callback(msg, level=Context.WARNING):
            if level == Context.WARNING:
                if msg in warnings:
                    return

                warnings.add(msg)
                if Qgis.QGIS_VERSION_INT >= 31602:
                    feedback.pushWarning("Warning: {}".format(msg))
                else:
                    feedback.reportError("Warning: {}".format(msg), False)

            elif level == Context.INFO:
                if msg in info:
                    return

                info.add(msg)
                feedback.pushInfo(msg)
            elif level == Context.CRITICAL:
                feedback.reportError(msg, False)

        conversion_context = Context()
        conversion_context.unsupported_object_callback = unsupported_object_callback
        conversion_context.project = context.project()
        conversion_context.can_place_annotations_in_main_annotation_layer = False

        try:
            LayerConverter.layers_to_qml(
                obj,
                input_file,
                output_file,
                on_error=on_error,
                context=conversion_context,
            )
        except NotImplementedException as e:
            feedback.reportError(str(e), fatalError=True)
            return {self.ERROR: str(e), self.CONVERTED: False, self.OUTPUT: None}

        return {self.OUTPUT: output_file, self.ERROR: None, self.CONVERTED: True}

    # pylint: enable=missing-docstring,unused-argument
