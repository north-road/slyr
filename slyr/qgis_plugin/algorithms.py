# -*- coding: utf-8 -*-
###############################################################################
#
# Copyright (C) 2018 Nyall Dawson, SMEC
#
# This source is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This code is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
###############################################################################

"""
SLYR QGIS Processing algorithms
"""

import os
from io import BytesIO
from qgis.core import (QgsProcessingAlgorithm,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingOutputNumber,
                       QgsStyle,
                       QgsColorRamp,
                       QgsSymbol,
                       QgsProcessingFeedback)
from qgis.PyQt.QtGui import QFontDatabase
from processing.core.ProcessingConfig import ProcessingConfig

from slyr.bintools.extractor import Extractor
from slyr.parser.stream import Stream
from slyr.parser.exceptions import (UnreadableSymbolException,
                                    InvalidColorException,
                                    UnsupportedVersionException,
                                    NotImplementedException,
                                    UnknownGuidException)
from slyr.converters.qgis import (Symbol_to_QgsSymbol,
                                  symbol_color_to_qcolor)


class StyleToQgisXml(QgsProcessingAlgorithm):
    """
    Converts .style databases to QGIS Style XML databases
    """

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'

    MARKER_SYMBOL_COUNT = 'MARKER_SYMBOL_COUNT'
    LINE_SYMBOL_COUNT = 'LINE_SYMBOL_COUNT'
    FILL_SYMBOL_COUNT = 'FILL_SYMBOL_COUNT'
    COLOR_RAMP_COUNT = 'COLOR_RAMP_COUNT'
    UNREADABLE_MARKER_SYMBOLS = 'UNREADABLE_MARKER_SYMBOLS'
    UNREADABLE_LINE_SYMBOLS = 'UNREADABLE_LINE_SYMBOLS'
    UNREADABLE_FILL_SYMBOLS = 'UNREADABLE_FILL_SYMBOLS'
    UNREADABLE_COLOR_RAMPS = 'UNREADABLE_COLOR_RAMPS'

    def createInstance(self):  # pylint: disable=missing-docstring
        return StyleToQgisXml()

    def name(self):  # pylint: disable=missing-docstring
        return 'styletoqgisxml'

    def displayName(self):  # pylint: disable=missing-docstring
        return 'Convert ESRI style to QGIS XML'

    def shortDescription(self):  # pylint: disable=missing-docstring
        return 'Converts ESRI style database to a QGIS XML Style library'

    def group(self):  # pylint: disable=missing-docstring
        return 'Style databases'

    def groupId(self):  # pylint: disable=missing-docstring
        return 'style'

    def shortHelpString(self):  # pylint: disable=missing-docstring
        return "Converts ESRI style database to a QGIS XML Style library"

    def initAlgorithm(self, config=None):  # pylint: disable=missing-docstring,unused-argument
        self.addParameter(QgsProcessingParameterFile(
            self.INPUT, 'Style database', extension='style'))

        self.addParameter(QgsProcessingParameterFileDestination(self.OUTPUT,
                                                                'Destination XML file', fileFilter="XML files (*.xml)"))

        self.addOutput(QgsProcessingOutputNumber(self.FILL_SYMBOL_COUNT, 'Fill Symbol Count'))
        self.addOutput(QgsProcessingOutputNumber(self.LINE_SYMBOL_COUNT, 'Line Symbol Count'))
        self.addOutput(QgsProcessingOutputNumber(self.MARKER_SYMBOL_COUNT, 'Marker Symbol Count'))
        self.addOutput(QgsProcessingOutputNumber(self.COLOR_RAMP_COUNT, 'Color Ramp Count'))
        self.addOutput(QgsProcessingOutputNumber(self.UNREADABLE_FILL_SYMBOLS, 'Unreadable Fill Symbol Count'))
        self.addOutput(QgsProcessingOutputNumber(self.UNREADABLE_LINE_SYMBOLS, 'Unreadable Line Symbol Count'))
        self.addOutput(QgsProcessingOutputNumber(self.UNREADABLE_MARKER_SYMBOLS, 'Unreadable Marker Symbol Count'))
        self.addOutput(QgsProcessingOutputNumber(self.UNREADABLE_COLOR_RAMPS, 'Unreadable Color Ramps'))

    def processAlgorithm(self, parameters, context, feedback):  # pylint: disable=missing-docstring,too-many-locals,too-many-statements,too-many-branches
        input_file = self.parameterAsString(parameters, self.INPUT, context)
        output_file = self.parameterAsFileOutput(parameters, self.OUTPUT, context)

        mdbtools_folder = ProcessingConfig.getSetting('MDB_PATH')

        style = QgsStyle()

        results = {}

        symbol_names = set()

        def make_name_unique(name):
            """
            Ensures that the symbol name is unique (in a case insensitive way)
            """
            counter = 0
            candidate = name
            while candidate.lower() in symbol_names:
                # make name unique
                if counter == 0:
                    candidate += '_1'
                else:
                    candidate = candidate[:candidate.rfind('_') + 1] + str(counter)
                counter += 1
            symbol_names.add(candidate.lower())
            return candidate

        for type_index, symbol_type in enumerate(
                (Extractor.FILL_SYMBOLS, Extractor.LINE_SYMBOLS, Extractor.MARKER_SYMBOLS, Extractor.COLOR_RAMPS)):
            feedback.pushInfo('Importing {} from {}'.format(symbol_type, input_file))

            raw_symbols = Extractor.extract_styles(input_file, symbol_type, mdbtools_path=mdbtools_folder)
            feedback.pushInfo('Found {} symbols of type "{}"\n\n'.format(len(raw_symbols), symbol_type))

            if feedback.isCanceled():
                break

            unreadable = 0
            for index, raw_symbol in enumerate(raw_symbols):
                feedback.setProgress(index / len(raw_symbols) * 33.3 + 33.3 * type_index)
                if feedback.isCanceled():
                    break
                name = raw_symbol[Extractor.NAME]
                feedback.pushInfo('{}/{}: {}'.format(index + 1, len(raw_symbols), name))

                unique_name = make_name_unique(name)
                if name != unique_name:
                    feedback.pushInfo('Corrected to unique name of {}'.format(unique_name))

                handle = BytesIO(raw_symbol[Extractor.BLOB])
                stream = Stream(handle)
                try:
                    symbol = stream.read_object()
                except UnreadableSymbolException as e:
                    feedback.reportError('Error reading symbol {}: {}'.format(name, e))
                    unreadable += 1
                    continue
                except NotImplementedException as e:
                    feedback.reportError('Parsing {} is not supported: {}'.format(name, e))
                    unreadable += 1
                    continue
                except UnsupportedVersionException as e:
                    feedback.reportError('Cannot read {} version: {}'.format(name, e))
                    unreadable += 1
                    continue
                except UnknownGuidException as e:
                    feedback.reportError(str(e))
                    unreadable += 1
                    continue

                try:
                    qgis_symbol = Symbol_to_QgsSymbol(symbol)
                except NotImplementedException as e:
                    feedback.reportError(str(e))
                    unreadable += 1
                    continue

                if isinstance(qgis_symbol, QgsSymbol):
                    self.check_for_missing_fonts(qgis_symbol, feedback)
                    style.addSymbol(unique_name, qgis_symbol)
                elif isinstance(qgis_symbol, QgsColorRamp):
                    style.addColorRamp(unique_name, qgis_symbol)

            if symbol_type == Extractor.FILL_SYMBOLS:
                results[self.FILL_SYMBOL_COUNT] = len(raw_symbols)
                results[self.UNREADABLE_FILL_SYMBOLS] = unreadable
            elif symbol_type == Extractor.LINE_SYMBOLS:
                results[self.LINE_SYMBOL_COUNT] = len(raw_symbols)
                results[self.UNREADABLE_LINE_SYMBOLS] = unreadable
            elif symbol_type == Extractor.MARKER_SYMBOLS:
                results[self.MARKER_SYMBOL_COUNT] = len(raw_symbols)
                results[self.UNREADABLE_MARKER_SYMBOLS] = unreadable
            elif symbol_type == Extractor.COLOR_RAMPS:
                results[self.COLOR_RAMP_COUNT] = len(raw_symbols)
                results[self.UNREADABLE_COLOR_RAMPS] = unreadable

        style.exportXml(output_file)
        results[self.OUTPUT] = output_file
        return results

    def check_for_missing_fonts(self, symbol: QgsSymbol, feedback: QgsProcessingFeedback):
        """
        Checks for missing (not installed) fonts, and warns
        """

        for l in symbol.symbolLayers():
            try:
                font = l.fontFamily()
            except AttributeError:
                continue

            if font not in QFontDatabase().families():
                feedback.reportError('Warning: font {} not available on system'.format(font))


class StyleToGpl(QgsProcessingAlgorithm):
    """
    Converts .style databases to GPL color palette files
    """

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'

    COLOR_COUNT = 'COLOR_COUNT'
    UNREADABLE_COLOR_COUNT = 'UNREADABLE_COLOR_COUNT'

    def createInstance(self):  # pylint: disable=missing-docstring
        return StyleToGpl()

    def name(self):  # pylint: disable=missing-docstring
        return 'styletogpl'

    def displayName(self):  # pylint: disable=missing-docstring
        return 'Convert ESRI style to GPL color palette'

    def shortDescription(self):  # pylint: disable=missing-docstring
        return 'Converts ESRI style database to a GPL format color palette file.'

    def group(self):  # pylint: disable=missing-docstring
        return 'Style databases'

    def groupId(self):  # pylint: disable=missing-docstring
        return 'style'

    def shortHelpString(self):  # pylint: disable=missing-docstring
        return "Converts ESRI style database to a GPL format color palette file, extracting all color entities " \
               "saved in the style."

    def initAlgorithm(self, config=None):  # pylint: disable=missing-docstring,unused-argument
        self.addParameter(QgsProcessingParameterFile(
            self.INPUT, 'Style database', extension='style'))

        self.addParameter(QgsProcessingParameterFileDestination(self.OUTPUT,
                                                                'Destination GPL file', fileFilter="GPL files (*.gpl)"))

        self.addOutput(QgsProcessingOutputNumber(self.COLOR_COUNT, 'Color Count'))
        self.addOutput(QgsProcessingOutputNumber(self.UNREADABLE_COLOR_COUNT, 'Unreadable Color Count'))

    def processAlgorithm(self, parameters, context, feedback):  # pylint: disable=missing-docstring,too-many-locals,too-many-statements
        input_file = self.parameterAsString(parameters, self.INPUT, context)
        output_file = self.parameterAsFileOutput(parameters, self.OUTPUT, context)

        mdbtools_folder = ProcessingConfig.getSetting('MDB_PATH')

        results = {}
        colors = []

        _, file_name = os.path.split(input_file)
        file_name, _ = os.path.splitext(file_name)

        feedback.pushInfo('Importing colors from {}'.format(input_file))

        raw_colors = Extractor.extract_styles(input_file, Extractor.COLORS, mdbtools_path=mdbtools_folder)
        feedback.pushInfo('Found {} colors'.format(len(raw_colors)))

        unreadable = 0
        for index, raw_color in enumerate(raw_colors):
            feedback.setProgress(index / len(raw_colors) * 100)
            if feedback.isCanceled():
                break

            name = raw_color[Extractor.NAME]
            feedback.pushInfo('{}/{}: {}'.format(index + 1, len(raw_colors), name))

            handle = BytesIO(raw_color[Extractor.BLOB])
            stream = Stream(handle)
            try:
                color = stream.read_object()
            except InvalidColorException:
                feedback.reportError('Error reading color {}'.format(name))
                unreadable += 1
                continue

            qcolor = symbol_color_to_qcolor(color)
            colors.append((name, qcolor))

        results[self.COLOR_COUNT] = len(raw_colors)
        results[self.UNREADABLE_COLOR_COUNT] = unreadable

        with open(output_file, 'wt') as f:
            f.write('GIMP Palette\n')
            f.write('Name: {}\n'.format(file_name))
            f.write('Columns: 4\n')
            f.write('#\n')
            for c in colors:
                f.write('{} {} {} {}\n'.format(c[1].red(), c[1].green(), c[1].blue(), c[0]))

        results[self.OUTPUT] = output_file
        return results
