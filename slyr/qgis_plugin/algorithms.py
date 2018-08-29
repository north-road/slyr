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

from io import BytesIO
from qgis.core import (QgsProcessingAlgorithm,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingOutputNumber,
                       QgsStyle)
from processing.core.ProcessingConfig import ProcessingConfig

from slyr.bintools.extractor import Extractor
from slyr.parser.symbol_parser import read_symbol, UnreadableSymbolException
from slyr.converters.qgis import FillSymbol_to_QgsFillSymbol, NotImplementedException


class StyleToQgisXml(QgsProcessingAlgorithm):
    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'

    MARKER_SYMBOL_COUNT = 'MARKER_SYMBOL_COUNT'
    LINE_SYMBOL_COUNT = 'LINE_SYMBOL_COUNT'
    FILL_SYMBOL_COUNT = 'FILL_SYMBOL_COUNT'
    UNREADABLE_MARKER_SYMBOLS = 'UNREADABLE_MARKER_SYMBOLS'
    UNREADABLE_LINE_SYMBOLS = 'UNREADABLE_LINE_SYMBOLS'
    UNREADABLE_FILL_SYMBOLS = 'UNREADABLE_FILL_SYMBOLS'

    def createInstance(self):
        return StyleToQgisXml()

    def name(self):
        return 'styletoqgisxml'

    def displayName(self):
        return 'Convert ESRI style to QGIS XML'

    def shortDescription(self):
        return 'Converts ESRI style database to a QGIS XML Style library'

    def group(self):
        return 'Style'

    def groupId(self):
        return 'style'

    def shortHelpString(self):
        return "Converts ESRI style database to a QGIS XML Style library"

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFile(
            self.INPUT, 'Style database', extension='style'))

        self.addParameter(QgsProcessingParameterFileDestination(self.OUTPUT,
                                                                'Destination XML file', fileFilter="XML files (*.xml)"))

        self.addOutput(QgsProcessingOutputNumber(self.FILL_SYMBOL_COUNT, 'Fill Symbol Count'))
        self.addOutput(QgsProcessingOutputNumber(self.LINE_SYMBOL_COUNT, 'Line Symbol Count'))
        self.addOutput(QgsProcessingOutputNumber(self.MARKER_SYMBOL_COUNT, 'Marker Symbol Count'))
        self.addOutput(QgsProcessingOutputNumber(self.UNREADABLE_FILL_SYMBOLS, 'Unreadable Fill Symbol Count'))
        self.addOutput(QgsProcessingOutputNumber(self.UNREADABLE_LINE_SYMBOLS, 'Unreadable Line Symbol Count'))
        self.addOutput(QgsProcessingOutputNumber(self.UNREADABLE_MARKER_SYMBOLS, 'Unreadable Marker Symbol Count'))

    def processAlgorithm(self, parameters, context, feedback):
        input_file = self.parameterAsString(parameters, self.INPUT, context)
        output_file = self.parameterAsFileOutput(parameters, self.OUTPUT, context)

        mdbtools_folder = ProcessingConfig.getSetting('MDB_PATH')

        style = QgsStyle()

        results = {}

        for type_index, symbol_type in enumerate((Extractor.FILL_SYMBOLS, Extractor.LINE_SYMBOLS, Extractor.MARKER_SYMBOLS)):
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
                feedback.pushInfo('{}/{}: {}'.format(index + 1, len(raw_symbols),name))

                handle = BytesIO(raw_symbol[Extractor.BLOB])
                try:
                    symbol = read_symbol(file_handle=handle)
                except UnreadableSymbolException:
                    feedback.reportError('Error reading symbol {}'.format(name))
                    unreadable += 1
                    continue

                try:
                    qgis_symbol = FillSymbol_to_QgsFillSymbol(symbol)
                except NotImplementedException as e:
                    feedback.reportError(str(e))
                    unreadable += 1
                    continue

                style.addSymbol(name, qgis_symbol)

            if symbol_type == Extractor.FILL_SYMBOLS:
                results[self.FILL_SYMBOL_COUNT] = len(raw_symbols)
                results[self.UNREADABLE_FILL_SYMBOLS] = unreadable
            elif symbol_type == Extractor.LINE_SYMBOLS:
                results[self.LINE_SYMBOL_COUNT] = len(raw_symbols)
                results[self.UNREADABLE_LINE_SYMBOLS] = unreadable
            elif symbol_type == Extractor.MARKER_SYMBOLS:
                results[self.MARKER_SYMBOL_COUNT] = len(raw_symbols)
                results[self.UNREADABLE_MARKER_SYMBOLS] = unreadable

        style.exportXml(output_file)
        results[self.OUTPUT] = output_file
        return results
