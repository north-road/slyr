"""
Extracts connection details from a .sde connection file
"""

# /***************************************************************************
#  *                                                                         *
#  *   This program is free software; you can redistribute it and/or modify  *
#  *   it under the terms of the GNU General Public License as published by  *
#  *   the Free Software Foundation; either version 2 of the License, or     *
#  *   (at your option) any later version.                                   *
#  *                                                                         *
#  ***************************************************************************/

import json

from qgis.core import (
    QgsProcessingParameterFile,
    QgsProcessingParameterFileDestination,
    QgsProcessingException,
)

from .algorithm import SlyrAlgorithm
from .utils import AlgorithmUtils
from ...parser.exceptions import (
    UnreadableSymbolException,
    NotImplementedException,
    UnknownClsidException,
    EmptyDocumentException,
    DocumentTypeException,
)
from ...parser.streams.sde_connection import SDEConnection


class ExtractSDEConnectionDetails(SlyrAlgorithm):
    """
    Extracts connection details from a .sde connection file
    """

    INPUT = "INPUT"
    OUTPUT = "OUTPUT"

    # pylint: disable=missing-docstring,unused-argument

    def createInstance(self):
        return ExtractSDEConnectionDetails()

    def name(self):
        return "extractsdedetails"

    def displayName(self):
        return "Extract SDE connection details"

    def shortDescription(self):
        return "Extracts the connection details from a .sde connection file."

    def group(self):
        return "SDE documents"

    def groupId(self):
        return "sde"

    def shortHelpString(self):
        return (
            "This algorithm extracts the connection details from "
            "a .sde connection file.\n\n"
            "Optionally, a JSON representation containing these "
            "details can be exported."
        )

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFile(
                self.INPUT,
                "Input SDE file",
                fileFilter="SDE Files (*.sde *.SDE);;All files (*.*)",
            )
        )

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT,
                "Destination JSON file",
                fileFilter="JSON files (*.json *.JSON);;All files (*.*)",
                optional=True,
                createByDefault=False,
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        input_file = self.parameterAsString(parameters, self.INPUT, context)
        output_file = self.parameterAsFileOutput(parameters, self.OUTPUT, context)

        with open(input_file, "rb") as f:
            try:
                doc = SDEConnection(f)
            except UnknownClsidException as e:
                feedback.reportError(str(e), fatalError=True)
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
            except EmptyDocumentException as e:
                raise QgsProcessingException(
                    "Cannot read {} - document is empty".format(input_file)
                ) from e
            except DocumentTypeException as e:
                raise QgsProcessingException(
                    "Cannot read {} - file is corrupt or not an SDE connection file".format(
                        input_file
                    )
                ) from e

            details = doc.to_dict()
            del details["type"]
            del details["version"]

            has_password = "PASSWORD" in details
            if has_password:
                del details["PASSWORD"]

            feedback.pushInfo("Connection details:")
            feedback.pushInfo("")
            for k, v in details.items():
                feedback.pushInfo(f"{k}: {v}")
            if has_password:
                feedback.reportError("Embedded password cannot be extracted!", False)

            feedback.pushInfo("")

            if output_file:
                res = json.dumps(
                    AlgorithmUtils.make_json_safe_dict(doc.to_dict()), indent=4
                )
                with open(output_file, "wt", encoding="utf8") as o:
                    o.write(res)

        return {ExtractSDEConnectionDetails.OUTPUT: output_file}

    # pylint: enable=missing-docstring,unused-argument
