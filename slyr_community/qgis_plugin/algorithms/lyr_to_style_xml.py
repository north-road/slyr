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
Converts .lyr to QGIS style XML
"""

from qgis.core import (Qgis,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterFileDestination,
                       QgsStyle,
                       QgsColorRamp,
                       QgsSymbol,
                       QgsTextFormat,
                       QgsProcessingException)

from .algorithm import SlyrAlgorithm
from ..gui_utils import GuiUtils
from ...converters.context import Context
from ...converters.layers import LayerConverter
from ...converters.vector_renderer import VectorRendererConverter
from ...parser.exceptions import (UnreadableSymbolException,
                                  NotImplementedException,
                                  UnknownClsidException,
                                  RequiresLicenseException)
from ...parser.objects.group_layer import GroupLayer
from ...parser.stream import Stream


class LyrToStyleXml(SlyrAlgorithm):
    """
    Converts .lyr to QGIS style XML
    """

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'

    # pylint: disable=missing-docstring,unused-argument

    def createInstance(self):
        return LyrToStyleXml()

    def name(self):
        return 'lyrtostylexml'

    def displayName(self):
        return 'Convert LYR to QGIS style XML'

    def shortDescription(self):
        return 'Converts an ESRI LYR file to a QGIS style XML file'

    def group(self):
        return 'LYR datasets'

    def groupId(self):
        return 'lyr'

    def shortHelpString(self):
        return "Converts an ESRI LYR file to a QGIS style XML file"

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFile(
            self.INPUT, 'Input LYR file', extension='lyr'))

        self.addParameter(QgsProcessingParameterFileDestination(
            self.OUTPUT, 'Destination style XML file', fileFilter='XML files (*.xml)'))

    def processAlgorithm(self,  # pylint: disable=too-many-locals,too-many-statements,too-many-branches
                         parameters,
                         context,
                         feedback):

        input_file = self.parameterAsString(parameters, self.INPUT, context)
        output_file = self.parameterAsFileOutput(parameters, self.OUTPUT, context)

        style = QgsStyle()
        style.createMemoryDatabase()

        warnings = set()

        def unsupported_object_callback(msg, level=Context.WARNING):
            if msg in warnings:
                return

            warnings.add(msg)
            if level == Context.WARNING:
                feedback.reportError('Warning: {}'.format(msg), False)
            elif level == Context.CRITICAL:
                feedback.reportError(msg, False)

        context = Context()
        context.unsupported_object_callback = unsupported_object_callback
        if Qgis.QGIS_VERSION_INT < 30600:
            context.invalid_layer_resolver = GuiUtils.get_valid_mime_uri
        # context.style_folder, _ = os.path.split(output_file)

        with open(input_file, 'rb') as f:
            stream = Stream(f, False, force_layer=True, offset=0)
            try:
                obj = stream.read_object()
            except RequiresLicenseException as e:
                raise QgsProcessingException('{} - please see https://north-road.com/slyr/ for details'.format(e)) from e
            except UnknownClsidException as e:
                feedback.reportError(str(e), fatalError=True)
                return {}
            except UnreadableSymbolException as e:
                feedback.reportError('Unreadable object: {}'.format(e), fatalError=True)
                return {}
            except NotImplementedException as e:
                feedback.reportError(str(e), fatalError=True)
                return {}
            except UnicodeDecodeError as e:
                feedback.reportError('Unreadable object: {}'.format(e), fatalError=True)
                return {}

        if not LayerConverter.is_layer(obj) and not isinstance(obj, GroupLayer):
            feedback.reportError('Objects of type {} are not supported'.format(obj.__class__.__name__),
                                 fatalError=False)
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
                    candidate += '_1'
                else:
                    candidate = candidate[:candidate.rfind('_') + 1] + str(counter)
                counter += 1
            symbol_names.add(candidate.lower())
            return candidate

        layers = LayerConverter.unique_layer_name_map(obj)
        for name, layer in layers.items():
            feedback.pushInfo('Extracting symbols from {}'.format(name))
            symbols = VectorRendererConverter.extract_symbols_from_renderer(layer, context, default_name=name,
                                                                            base_name=name if len(layers) > 1 else '')

            for k, v in symbols.items():
                unique_name = make_name_unique(k)
                if k != unique_name:
                    feedback.pushInfo('Corrected to unique name of {}'.format(unique_name))

                if isinstance(v, QgsSymbol):
                    style.addSymbol(unique_name, v, True)
                elif isinstance(v, QgsColorRamp):
                    style.addColorRamp(unique_name, v, True)
                elif isinstance(v, QgsTextFormat):
                    if Qgis.QGIS_VERSION_INT >= 30900:
                        style.addTextFormat(unique_name, v, True)

        style.exportXml(output_file)
        return {self.OUTPUT: output_file}

    # pylint: enable=missing-docstring,unused-argument
