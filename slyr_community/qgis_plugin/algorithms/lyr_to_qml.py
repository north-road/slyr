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
Converts .lyr to QML
"""

from qgis.core import (Qgis,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingOutputString)

from .algorithm import SlyrAlgorithm
from ..gui_utils import GuiUtils
from ...converters.context import Context
from ...converters.layers import LayerConverter
from ...parser.exceptions import (UnreadableSymbolException,
                                  NotImplementedException,
                                  UnknownClsidException)
from ...parser.objects.group_layer import GroupLayer
from ...parser.stream import Stream

try:
    from qgis.core import QgsProcessingOutputBoolean  # pylint: disable=ungrouped-imports
except ImportError:
    QgsProcessingOutputBoolean = None


class LyrToQml(SlyrAlgorithm):
    """
    Converts .lyr to QML
    """

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    CONVERTED = 'CONVERTED'
    ERROR = 'ERROR'

    # pylint: disable=missing-docstring,unused-argument

    def createInstance(self):
        return LyrToQml()

    def name(self):
        return 'lyrtoqml'

    def displayName(self):
        return 'Convert LYR to QML'

    def shortDescription(self):
        return 'Converts an ESRI LYR file to a QGIS QML file (or files)'

    def group(self):
        return 'LYR datasets'

    def groupId(self):
        return 'lyr'

    def shortHelpString(self):
        return "Converts an ESRI LYR file to a QGIS QML file. If multiple layers are present in the LYR file, each will be converted to an individual QML file."

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFile(
            self.INPUT, 'Input LYR file', extension='lyr'))

        self.addParameter(QgsProcessingParameterFileDestination(
            self.OUTPUT, 'Destination QML file', fileFilter='QML files (*.qml)'))

        if QgsProcessingOutputBoolean is not None:
            self.addOutput(QgsProcessingOutputBoolean(self.CONVERTED, 'Converted'))
        self.addOutput(QgsProcessingOutputString(self.ERROR, 'Error message'))

    def processAlgorithm(self,  # pylint: disable=too-many-locals,too-many-statements,too-many-return-statements
                         parameters,
                         context,
                         feedback):
        input_file = self.parameterAsString(parameters, self.INPUT, context)
        output_file = self.parameterAsFileOutput(parameters, self.OUTPUT, context)

        warnings = set()
        with open(input_file, 'rb') as f:
            stream = Stream(f, False, force_layer=True, offset=0)
            try:
                obj = stream.read_object()
            except UnknownClsidException as e:
                feedback.reportError(str(e), fatalError=True)
                return {
                    self.ERROR: str(e),
                    self.CONVERTED: False,
                    self.OUTPUT: None
                }
            except UnreadableSymbolException as e:
                err = 'Unreadable object: {}'.format(e)
                feedback.reportError(err, fatalError=True)
                return {
                    self.ERROR: err,
                    self.CONVERTED: False,
                    self.OUTPUT: None
                }
            except NotImplementedException as e:
                feedback.reportError(str(e), fatalError=True)
                return {
                    self.ERROR: str(e),
                    self.CONVERTED: False,
                    self.OUTPUT: None
                }
            except UnicodeDecodeError as e:
                err = 'Unreadable object: {}'.format(e)
                feedback.reportError(err, fatalError=True)
                return {
                    self.ERROR: err,
                    self.CONVERTED: False,
                    self.OUTPUT: None
                }

        if not LayerConverter.is_layer(obj) and not isinstance(obj, GroupLayer):
            err = 'Objects of type {} are not supported'.format(obj.__class__.__name__)
            feedback.reportError(err,
                                 fatalError=False)
            return {
                self.ERROR: err,
                self.CONVERTED: False,
                self.OUTPUT: None
            }

        def on_error(error):
            feedback.reportError(error, fatalError=False)

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
        try:
            LayerConverter.layers_to_qml(obj, input_file, output_file, on_error=on_error, context=context)
        except NotImplementedException as e:
            feedback.reportError(str(e), fatalError=True)
            return {
                self.ERROR: str(e),
                self.CONVERTED: False,
                self.OUTPUT: None
            }

        return {
            self.OUTPUT: output_file,
            self.ERROR: None,
            self.CONVERTED: True
        }

    # pylint: enable=missing-docstring,unused-argument
