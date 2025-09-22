"""
Adds layers from an MXD document to the current project
"""

# /***************************************************************************
#  *                                                                         *
#  *   This program is free software; you can redistribute it and/or modify  *
#  *   it under the terms of the GNU General Public License as published by  *
#  *   the Free Software Foundation; either version 2 of the License, or     *
#  *   (at your option) any later version.                                   *
#  *                                                                         *
#  ***************************************************************************/

from qgis.core import Qgis, QgsProcessingParameterFile, QgsProcessingFeedback

from .algorithm import SlyrAlgorithm
from ...converters.context import Context
from ...converters.project import ProjectConverter
from ...parser.exceptions import (
    UnreadableSymbolException,
    NotImplementedException,
    UnknownClsidException,
)
from ...parser.objects.map import Map
from ...parser.stream import Stream
from ...parser.exceptions import RequiresLicenseException


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
        self.input_file = self.parameterAsString(parameters, self.INPUT, context)

        with open(self.input_file, "rb") as f:
            stream = Stream(f, False, force_layer=True, offset=-1)
            try:
                self.obj = stream.read_object()
            except UnknownClsidException:
                feedback.reportError(
                    "This document requires the licensed version of SLYR to convert - please see https://north-road.com/slyr/ for details",
                    fatalError=True,
                )
                return {}
            except UnreadableSymbolException as e:
                feedback.reportError("Unreadable object: {}".format(e), fatalError=True)
                return {}
            except NotImplementedException as e:
                feedback.reportError(str(e), fatalError=True)
                return {}
            except UnicodeDecodeError as e:
                feedback.reportError("Unreadable object: {}".format(e), fatalError=True)
                return {}
            except RequiresLicenseException:
                feedback.reportError(
                    "This document requires the licensed version of SLYR to convert - please see https://north-road.com/slyr/ for details",
                    fatalError=True,
                )
                return {}

            if not isinstance(self.obj, Map):
                feedback.reportError(
                    "Expected Map object, found: {}".format(
                        self.obj.__class__.__name__
                    ),
                    fatalError=True,
                )
                return {}

        return {}

    def postProcessAlgorithm(self, context, feedback: QgsProcessingFeedback):
        if self.obj:
            conversion_context = Context()
            conversion_context.project = context.project()

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

            conversion_context.unsupported_object_callback = unsupported_object_callback

            ProjectConverter.add_layers_to_project(
                context.project(), self.input_file, self.obj, conversion_context
            )
        return {}

    # pylint: enable=missing-docstring,unused-argument
