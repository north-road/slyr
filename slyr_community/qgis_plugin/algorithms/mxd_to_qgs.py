"""
Converts an MXD document to a QGS project file
"""

# /***************************************************************************
#  *                                                                         *
#  *   This program is free software; you can redistribute it and/or modify  *
#  *   it under the terms of the GNU General Public License as published by  *
#  *   the Free Software Foundation; either version 2 of the License, or     *
#  *   (at your option) any later version.                                   *
#  *                                                                         *
#  ***************************************************************************/

from pathlib import PureWindowsPath, Path

from qgis.core import (
    Qgis,
    QgsProcessingParameterFile,
    QgsProcessingParameterFileDestination,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterDefinition,
    QgsProcessingException,
)

from .algorithm import SlyrAlgorithm
from ...converters.context import Context
from ...converters.project import ProjectConverter
from ...parser.exceptions import (
    UnreadableSymbolException,
    NotImplementedException,
    UnknownClsidException,
    EmptyDocumentException,
    DocumentTypeException,
)
from ...parser.streams.map_document import MapDocument
from ...parser.exceptions import RequiresLicenseException


class ConvertMxdToQgs(SlyrAlgorithm):
    """
    Converts an MXD document to a QGS project file
    """

    INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    TEST_MODE = "TEST_MODE"

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
        self.addParameter(
            QgsProcessingParameterFile(
                self.INPUT,
                "Input MXD/MXT file",
                fileFilter="MXD/MXT Documents (*.mxd *.MXD *.mxt *.MXT)",
            )
        )

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

    def autogenerateParameterValues(self, rowParameters, changedParameter, mode):
        if changedParameter == self.INPUT:
            input_file = rowParameters.get(self.INPUT)
            if input_file:
                input_path = Path(input_file)
                if input_path.exists():
                    return {self.OUTPUT: input_path.with_suffix(".qgs").as_posix()}

        return {}

    def processAlgorithm(self, parameters, context, feedback):
        input_file = self.parameterAsString(parameters, self.INPUT, context)
        output_file = self.parameterAsFileOutput(parameters, self.OUTPUT, context)
        test_mode = self.parameterAsBool(parameters, self.TEST_MODE, context)

        slyr_context = Context()
        slyr_context.ignore_online_sources = test_mode
        p = self.convert_project(input_file, feedback, slyr_context)
        if p and not test_mode and not p.write(output_file):
            raise QgsProcessingException(
                "Error writing to output file: {}".format(p.error())
            )

        return {ConvertMxdToQgs.OUTPUT: output_file}

    # pylint: enable=missing-docstring,unused-argument

    @staticmethod
    def convert_project(input_file, feedback, slyr_context: Context):
        """
        Converts an MXD project
        """
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

        slyr_context.unsupported_object_callback = unsupported_object_callback

        with open(input_file, "rb") as f:
            try:
                doc = MapDocument(f, read_layouts=True)
            except UnknownClsidException:
                feedback.reportError(
                    "This document requires the licensed version of SLYR to convert - please see https://north-road.com/slyr/ for details",
                    fatalError=True,
                )
                return {}
            except RequiresLicenseException as e:
                raise QgsProcessingException(
                    "{} - please see https://north-road.com/slyr/ for details".format(e)
                ) from e
            except UnreadableSymbolException as e:
                feedback.reportError("Unreadable object: {}".format(e), fatalError=True)
                return {}
            except NotImplementedException as e:
                feedback.reportError(str(e), fatalError=True)
                return {}
            except UnicodeDecodeError as e:
                feedback.reportError("Unreadable object: {}".format(e), fatalError=True)
                return {}
            except EmptyDocumentException as e:
                raise QgsProcessingException(
                    "Cannot read {} - document is empty".format(input_file)
                ) from e
            except DocumentTypeException as e:
                raise QgsProcessingException(
                    "Cannot read {} - file is corrupt or not an MXD document".format(
                        input_file
                    )
                ) from e

            if doc.original_path:
                slyr_context.original_path = PureWindowsPath(doc.original_path).parent

            p = ProjectConverter.convert_project(input_file, doc, context=slyr_context)
            return p
