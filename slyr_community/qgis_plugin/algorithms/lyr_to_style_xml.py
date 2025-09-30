"""
Converts .lyr to QGIS style XML
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
    QgsStyle,
    QgsColorRamp,
    QgsSymbol,
    QgsTextFormat,
)

from .algorithm import SlyrAlgorithm
from ...converters.context import Context
from ...converters.layers import LayerConverter
from ...converters.vector_renderer import VectorRendererConverter
from ...parser.exceptions import (
    UnreadableSymbolException,
    NotImplementedException,
    UnknownClsidException,
)
from ...parser.objects.group_layer import GroupLayer
from ...parser.stream import Stream
from qgis.core import QgsProcessingException
from ...parser.exceptions import RequiresLicenseException


class LyrToStyleXml(SlyrAlgorithm):
    """
    Converts .lyr to QGIS style XML
    """

    INPUT = "INPUT"
    OUTPUT = "OUTPUT"

    # pylint: disable=missing-docstring,unused-argument

    def createInstance(self):
        return LyrToStyleXml()

    def name(self):
        return "lyrtostylexml"

    def displayName(self):
        return "Convert LYR to QGIS style XML"

    def shortDescription(self):
        return "Converts an ESRI LYR file to a QGIS style XML file"

    def group(self):
        return "LYR datasets"

    def groupId(self):
        return "lyr"

    def shortHelpString(self):
        return "Converts an ESRI LYR file to a QGIS style XML file"

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFile(self.INPUT, "Input LYR file", extension="lyr")
        )

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT,
                "Destination style XML file",
                fileFilter="XML files (*.xml)",
            )
        )

    def autogenerateParameterValues(self, rowParameters, changedParameter, mode):
        if changedParameter == self.INPUT:
            input_file = rowParameters.get(self.INPUT)
            if input_file:
                input_path = Path(input_file)
                if input_path.exists():
                    return {self.OUTPUT: input_path.with_suffix(".xml").as_posix()}

        return {}

    def processAlgorithm(
        self,  # pylint: disable=too-many-locals,too-many-statements,too-many-branches
        parameters,
        context,
        feedback,
    ):
        input_file = self.parameterAsString(parameters, self.INPUT, context)
        output_file = self.parameterAsFileOutput(parameters, self.OUTPUT, context)

        style = QgsStyle()
        style.createMemoryDatabase()

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
        conversion_context.unsupported_object_callback = unsupported_object_callback
        conversion_context.can_place_annotations_in_main_annotation_layer = False

        with open(input_file, "rb") as f:
            stream = Stream(f, False, force_layer=True, offset=0)
            try:
                obj = stream.read_object()
            except UnknownClsidException as e:
                feedback.reportError(str(e), fatalError=True)
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

        if not LayerConverter.is_layer(obj) and not isinstance(obj, GroupLayer):
            feedback.reportError(
                "Objects of type {} are not supported".format(obj.__class__.__name__),
                fatalError=False,
            )
            return {}

        symbol_names = set()

        def make_name_unique(original_name):
            """
            Ensures that the symbol name is unique (in a case-insensitive way)
            """
            counter = 0
            candidate = original_name
            while candidate.lower() in symbol_names:
                # make name unique
                if counter == 0:
                    candidate += "_1"
                else:
                    candidate = candidate[: candidate.rfind("_") + 1] + str(counter)
                counter += 1
            symbol_names.add(candidate.lower())
            return candidate

        layers = LayerConverter.unique_layer_name_map(obj)
        for name, layer in layers.items():
            feedback.pushInfo("Extracting symbols from {}".format(name))
            symbols = VectorRendererConverter.extract_symbols_from_renderer(
                layer,
                conversion_context,
                default_name=name,
                base_name=name if len(layers) > 1 else "",
            )

            for k, v in symbols.items():
                unique_name = make_name_unique(k)
                if k != unique_name:
                    feedback.pushInfo(
                        "Corrected to unique name of {}".format(unique_name)
                    )

                if isinstance(v, QgsSymbol):
                    style.addSymbol(unique_name, v, True)
                elif isinstance(v, QgsColorRamp):
                    style.addColorRamp(unique_name, v, True)
                elif isinstance(v, QgsTextFormat):
                    style.addTextFormat(unique_name, v, True)

        style.exportXml(output_file)
        return {self.OUTPUT: output_file}

    # pylint: enable=missing-docstring,unused-argument
