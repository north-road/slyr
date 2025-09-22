"""
Converts .lyr to QLR
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
    QgsProcessingParameterBoolean,
    QgsProcessingParameterDefinition,
    QgsProcessingOutputString,
    QgsProcessingException,
)

from .algorithm import SlyrAlgorithm
from ...converters.context import Context
from ...converters.layers import LayerConverter
from ...parser.exceptions import (
    UnreadableSymbolException,
    UnsupportedVersionException,
    NotImplementedException,
    UnknownClsidException,
    EmptyDocumentException,
    DocumentTypeException,
)
from ...parser.objects.base_map_layer import BaseMapLayer
from ...parser.objects.group_layer import GroupLayer
from ...parser.streams.layer import LayerFile
from ...parser.exceptions import RequiresLicenseException

try:
    from qgis.core import QgsProcessingOutputBoolean  # pylint: disable=ungrouped-imports
except ImportError:
    QgsProcessingOutputBoolean = None


class LyrToQlr(SlyrAlgorithm):
    """
    Converts .lyr to QLR
    """

    INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    USE_RELATIVE_PATHS = "USE_RELATIVE_PATHS"
    TEST_MODE = "TEST_MODE"
    CONVERTED = "CONVERTED"
    ERROR = "ERROR"

    # pylint: disable=missing-docstring,unused-argument

    def createInstance(self):
        return LyrToQlr()

    def name(self):
        return "lyrtoqlr"

    def displayName(self):
        return "Convert LYR to QLR"

    def shortDescription(self):
        return "Converts an ESRI LYR file to a QGIS QLR file"

    def group(self):
        return "LYR datasets"

    def groupId(self):
        return "lyr"

    def shortHelpString(self):
        return "Converts an ESRI LYR file to a QGIS QLR file"

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFile(self.INPUT, "Input LYR file", extension="lyr")
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.USE_RELATIVE_PATHS, "Store relative paths", defaultValue=False
            )
        )

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT, "Destination QLR file", fileFilter="QLR files (*.qlr)"
            )
        )

        param_test_mode = QgsProcessingParameterBoolean(
            self.TEST_MODE, "Test mode (debug option)", False, True
        )
        param_test_mode.setFlags(
            param_test_mode.flags() | QgsProcessingParameterDefinition.Flag.FlagHidden
        )
        self.addParameter(param_test_mode)

        if QgsProcessingOutputBoolean is not None:
            self.addOutput(QgsProcessingOutputBoolean(self.CONVERTED, "Converted"))
        self.addOutput(QgsProcessingOutputString(self.ERROR, "Error message"))

    def autogenerateParameterValues(self, rowParameters, changedParameter, mode):
        if changedParameter == self.INPUT:
            input_file = rowParameters.get(self.INPUT)
            if input_file:
                input_path = Path(input_file)
                if input_path.exists():
                    return {self.OUTPUT: input_path.with_suffix(".qlr").as_posix()}

        return {}

    def processAlgorithm(
        self,  # pylint: disable=too-many-locals,too-many-statements,too-many-return-statements
        parameters,
        context,
        feedback,
    ):
        input_file = self.parameterAsString(parameters, self.INPUT, context)
        output_file = self.parameterAsFileOutput(parameters, self.OUTPUT, context)
        test_mode = self.parameterAsBool(parameters, self.TEST_MODE, context)

        use_relative_paths = self.parameterAsBool(
            parameters, self.USE_RELATIVE_PATHS, context
        )

        warnings = set()
        info = set()

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
        conversion_context.project = context.project()
        conversion_context.can_place_annotations_in_main_annotation_layer = False
        conversion_context.unsupported_object_callback = unsupported_object_callback
        conversion_context.ignore_online_sources = test_mode

        with open(input_file, "rb") as f:
            try:
                doc = LayerFile(f)
            except UnknownClsidException as e:
                feedback.reportError(str(e), fatalError=True)
                return {self.ERROR: str(e), self.CONVERTED: False, self.OUTPUT: None}
            except RequiresLicenseException as e:
                raise QgsProcessingException(
                    "{} - please see https://north-road.com/slyr/ for details".format(e)
                ) from e
            except UnreadableSymbolException as e:
                feedback.reportError("Unreadable object: {}".format(e), fatalError=True)
                return {self.ERROR: str(e), self.CONVERTED: False, self.OUTPUT: None}
            except UnsupportedVersionException as e:
                err = "Unsupported version: {}".format(e)
                feedback.reportError(err, fatalError=True)
                return {self.ERROR: err, self.CONVERTED: False, self.OUTPUT: None}
            except NotImplementedException as e:
                feedback.reportError(str(e), fatalError=True)
                return {self.ERROR: str(e), self.CONVERTED: False, self.OUTPUT: None}
            except UnicodeDecodeError as e:
                err = "Unreadable object: {}".format(e)
                feedback.reportError(err, fatalError=True)
                return {self.ERROR: err, self.CONVERTED: False, self.OUTPUT: None}
            except EmptyDocumentException as e:
                raise QgsProcessingException(
                    "Cannot read {} - document is empty".format(input_file)
                ) from e
            except DocumentTypeException as e:
                raise QgsProcessingException(
                    "Cannot read {} - file is corrupt or not an LYR document".format(
                        input_file
                    )
                ) from e

            obj = doc.root

        if (
            not LayerConverter.is_layer(obj)
            and not isinstance(obj, GroupLayer)
            and not isinstance(obj, BaseMapLayer)
        ):
            err = "Objects of type {} are not supported".format(obj.__class__.__name__)
            feedback.reportError(err, fatalError=False)
            return {self.ERROR: err, self.CONVERTED: False, self.OUTPUT: None}

        try:
            res, error = LayerConverter.object_to_qlr(
                obj,
                input_file,
                output_file,
                conversion_context,
                use_relative_paths=use_relative_paths,
            )
        except NotImplementedException as e:
            feedback.reportError(str(e), fatalError=True)
            return {self.ERROR: str(e), self.CONVERTED: False, self.OUTPUT: None}

        if not res:
            raise QgsProcessingException(error)

        return {self.OUTPUT: output_file, self.ERROR: None, self.CONVERTED: True}

    # pylint: enable=missing-docstring,unused-argument
