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
Converts .style databases to QGIS Style XML databases
"""

import os
from io import BytesIO

from qgis.PyQt.QtCore import QVariant
from qgis.core import (Qgis,
                       QgsProcessing,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingOutputNumber,
                       QgsProcessingException,
                       QgsStyle,
                       QgsFeature,
                       QgsFields,
                       QgsField,
                       QgsColorRamp,
                       QgsSymbol,
                       QgsTextFormat,
                       QgsPalLayerSettings)

from .algorithm import SlyrAlgorithm
from ...bintools.extractor import Extractor, MissingBinaryException
from ...converters.context import Context
from ...converters.symbols import SymbolConverter
from ...parser.exceptions import (UnreadableSymbolException,
                                  UnsupportedVersionException,
                                  NotImplementedException,
                                  UnknownClsidException,
                                  UnreadablePictureException)
from ...parser.stream import Stream

try:
    from qgis.core import QgsLegendPatchShape  # pylint: disable=ungrouped-imports
except ImportError:
    QgsLegendPatchShape = None


class StyleToQgisXml(SlyrAlgorithm):
    """
    Converts .style databases to QGIS Style XML databases
    """

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    REPORT = 'REPORT'

    MARKER_SYMBOL_COUNT = 'MARKER_SYMBOL_COUNT'
    LINE_SYMBOL_COUNT = 'LINE_SYMBOL_COUNT'
    FILL_SYMBOL_COUNT = 'FILL_SYMBOL_COUNT'
    COLOR_RAMP_COUNT = 'COLOR_RAMP_COUNT'
    TEXT_FORMAT_COUNT = 'TEXT_FORMAT_COUNT'
    LABEL_SETTINGS_COUNT = 'LABEL_SETTINGS_COUNT'
    LINE_PATCH_COUNT = 'LINE_PATCH_COUNT'
    AREA_PATCH_COUNT = 'AREA_PATCH_COUNT'
    UNREADABLE_MARKER_SYMBOLS = 'UNREADABLE_MARKER_SYMBOLS'
    UNREADABLE_LINE_SYMBOLS = 'UNREADABLE_LINE_SYMBOLS'
    UNREADABLE_FILL_SYMBOLS = 'UNREADABLE_FILL_SYMBOLS'
    UNREADABLE_COLOR_RAMPS = 'UNREADABLE_COLOR_RAMPS'
    UNREADABLE_TEXT_FORMATS = 'UNREADABLE_TEXT_FORMATS'
    UNREADABLE_LABEL_SETTINGS = 'UNREADABLE_LABEL_SETTINGS'
    UNREADABLE_LINE_PATCHES = 'UNREADABLE_LINE_PATCHES'
    UNREADABLE_AREA_PATCHES = 'UNREADABLE_AREA_PATCHES'

    # pylint: disable=missing-docstring,unused-argument

    def createInstance(self):
        return StyleToQgisXml()

    def name(self):
        return 'styletoqgisxml'

    def displayName(self):
        return 'Convert ESRI style to QGIS style XML'

    def shortDescription(self):
        return 'Converts ESRI style database to a QGIS XML Style library'

    def canExecute(self):
        res, error = super().canExecute()
        if not res:
            return False, error

        if not Extractor.is_mdb_tools_binary_available():
            return False, 'The MDB tools "mdb-export" utility is required to convert .style databases. Please setup a path to the MDB tools utility in the Settings - Options dialog, under the SLYR tab.'

        return True, None

    def group(self):
        return 'Style databases'

    def groupId(self):
        return 'style'

    def shortHelpString(self):
        return "Converts ESRI style database to a QGIS XML Style library"

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFile(
            self.INPUT, 'Style database', extension='style'))

        self.addParameter(QgsProcessingParameterFileDestination(self.OUTPUT,
                                                                'Destination XML file', fileFilter="XML files (*.xml)"))

        self.addParameter(QgsProcessingParameterFeatureSink(self.REPORT, 'Unconvertable symbols report',
                                                            QgsProcessing.TypeVector, None, True, False))

        self.addOutput(QgsProcessingOutputNumber(self.FILL_SYMBOL_COUNT, 'Fill Symbol Count'))
        self.addOutput(QgsProcessingOutputNumber(self.LINE_SYMBOL_COUNT, 'Line Symbol Count'))
        self.addOutput(QgsProcessingOutputNumber(self.MARKER_SYMBOL_COUNT, 'Marker Symbol Count'))
        self.addOutput(QgsProcessingOutputNumber(self.COLOR_RAMP_COUNT, 'Color Ramp Count'))
        self.addOutput(QgsProcessingOutputNumber(self.TEXT_FORMAT_COUNT, 'Text Format Count'))
        self.addOutput(QgsProcessingOutputNumber(self.LINE_PATCH_COUNT, 'Line Patch Count'))
        self.addOutput(QgsProcessingOutputNumber(self.AREA_PATCH_COUNT, 'Area Patch Count'))
        self.addOutput(QgsProcessingOutputNumber(self.UNREADABLE_FILL_SYMBOLS, 'Unreadable Fill Symbol Count'))
        self.addOutput(QgsProcessingOutputNumber(self.UNREADABLE_LINE_SYMBOLS, 'Unreadable Line Symbol Count'))
        self.addOutput(QgsProcessingOutputNumber(self.UNREADABLE_MARKER_SYMBOLS, 'Unreadable Marker Symbol Count'))
        self.addOutput(QgsProcessingOutputNumber(self.UNREADABLE_COLOR_RAMPS, 'Unreadable Color Ramps'))
        self.addOutput(QgsProcessingOutputNumber(self.UNREADABLE_TEXT_FORMATS, 'Unreadable Text Formats'))
        self.addOutput(QgsProcessingOutputNumber(self.UNREADABLE_LINE_PATCHES, 'Unreadable Line Patches'))
        self.addOutput(QgsProcessingOutputNumber(self.UNREADABLE_AREA_PATCHES, 'Unreadable Area Patches'))

    def processAlgorithm(self,  # pylint:disable=too-many-locals,too-many-statements,too-many-branches
                         parameters,
                         context,
                         feedback):
        input_file = self.parameterAsString(parameters, self.INPUT, context)
        output_file = self.parameterAsFileOutput(parameters, self.OUTPUT, context)

        fields = QgsFields()
        fields.append(QgsField('name', QVariant.String, '', 60))
        fields.append(QgsField('warning', QVariant.String, '', 250))

        sink, dest = self.parameterAsSink(parameters, self.REPORT, context, fields)

        style = QgsStyle()
        style.createMemoryDatabase()

        results = {}

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

        symbols_to_extract = [Extractor.FILL_SYMBOLS, Extractor.LINE_SYMBOLS, Extractor.MARKER_SYMBOLS,
                              Extractor.COLOR_RAMPS, Extractor.LINE_PATCHES, Extractor.AREA_PATCHES]
        if Qgis.QGIS_VERSION_INT >= 30900:
            symbols_to_extract.extend((Extractor.TEXT_SYMBOLS, Extractor.LABELS, Extractor.MAPLEX_LABELS))

        type_percent = 100.0 / len(symbols_to_extract)

        results[self.LABEL_SETTINGS_COUNT] = 0
        results[self.UNREADABLE_LABEL_SETTINGS] = 0

        for type_index, symbol_type in enumerate(symbols_to_extract):
            feedback.pushInfo('Importing {} from {}'.format(symbol_type, input_file))

            try:
                raw_symbols = Extractor.extract_styles(input_file, symbol_type)
            except MissingBinaryException:
                raise QgsProcessingException(  # pylint: disable=raise-missing-from
                    'The MDB tools "mdb-export" utility is required to convert .style databases. Please setup a path to the MDB tools utility in the SLYR options panel.')

            feedback.pushInfo('Found {} symbols of type "{}"\n\n'.format(len(raw_symbols), symbol_type))

            if feedback.isCanceled():
                break

            unreadable = 0
            for index, raw_symbol in enumerate(raw_symbols):
                feedback.setProgress(index / len(raw_symbols) * type_percent + type_percent * type_index)
                if feedback.isCanceled():
                    break
                name = raw_symbol[Extractor.NAME]
                tags = raw_symbol[Extractor.TAGS].split(';')
                feedback.pushInfo('{}/{}: {}'.format(index + 1, len(raw_symbols), name))

                unique_name = make_name_unique(name)
                if name != unique_name:
                    feedback.pushInfo('Corrected to unique name of {}'.format(unique_name))

                handle = BytesIO(raw_symbol[Extractor.BLOB])
                stream = Stream(handle)

                f = QgsFeature()
                try:
                    symbol = stream.read_object()
                except UnreadableSymbolException as e:
                    feedback.reportError('Error reading symbol {}: {}'.format(name, e), False)
                    unreadable += 1
                    if sink:
                        f.setAttributes([name, 'Error reading symbol: {}'.format(e)])
                        sink.addFeature(f)
                    continue
                except NotImplementedException as e:
                    feedback.reportError('Parsing {} is not supported: {}'.format(name, e), False)
                    unreadable += 1
                    if sink:
                        f.setAttributes([name, 'Parsing not supported: {}'.format(e)])
                        sink.addFeature(f)
                    continue
                except UnsupportedVersionException as e:
                    feedback.reportError('Cannot read {} version: {}'.format(name, e), False)
                    unreadable += 1
                    if sink:
                        f.setAttributes([name, 'Version not supported: {}'.format(e)])
                        sink.addFeature(f)
                    continue
                except UnknownClsidException as e:
                    feedback.reportError(str(e), False)
                    unreadable += 1
                    if sink:
                        f.setAttributes([name, 'Unknown object: {}'.format(e)])
                        sink.addFeature(f)
                    continue
                except UnreadablePictureException as e:
                    feedback.reportError(str(e), False)
                    unreadable += 1
                    if sink:
                        f.setAttributes([name, 'Unreadable picture: {}'.format(e)])
                        sink.addFeature(f)
                    continue

                def unsupported_object_callback(msg, level=Context.WARNING):
                    if level == Context.WARNING:
                        feedback.reportError('Warning: {}'.format(msg), False)
                    elif level == Context.CRITICAL:
                        feedback.reportError(msg, False)

                    if sink:
                        feat = QgsFeature()
                        feat.setAttributes([name, msg])  # pylint: disable=cell-var-from-loop
                        sink.addFeature(feat)

                context = Context()
                context.symbol_name = unique_name
                context.style_folder, _ = os.path.split(output_file)
                context.unsupported_object_callback = unsupported_object_callback

                if symbol_type in (Extractor.AREA_PATCHES, Extractor.LINE_PATCHES):
                    feedback.reportError('{}: Legend patch conversion requires the licensed version of SLYR'.format(name),
                                         False)
                    unreadable += 1
                    if sink:
                        f.setAttributes([name, 'Unreadable legend patch: {}'.format(name)])
                        sink.addFeature(f)
                    continue
                else:
                    try:
                        qgis_symbol = SymbolConverter.Symbol_to_QgsSymbol(symbol, context)

                    except NotImplementedException as e:
                        feedback.reportError(str(e), False)
                        unreadable += 1
                        if sink:
                            f.setAttributes([name, str(e)])
                            sink.addFeature(f)
                        continue
                    except UnreadablePictureException as e:
                        feedback.reportError(str(e), False)
                        unreadable += 1
                        if sink:
                            f.setAttributes([name, 'Unreadable picture: {}'.format(e)])
                            sink.addFeature(f)
                        continue

                if isinstance(qgis_symbol, QgsSymbol):
                    style.addSymbol(unique_name, qgis_symbol, True)
                elif isinstance(qgis_symbol, QgsColorRamp):
                    style.addColorRamp(unique_name, qgis_symbol, True)
                elif isinstance(qgis_symbol, QgsTextFormat):
                    if Qgis.QGIS_VERSION_INT >= 30900:
                        style.addTextFormat(unique_name, qgis_symbol, True)
                elif isinstance(qgis_symbol, QgsPalLayerSettings):
                    if Qgis.QGIS_VERSION_INT >= 30900:
                        style.addLabelSettings(unique_name, qgis_symbol, True)
                elif Qgis.QGIS_VERSION_INT >= 31300:
                    if isinstance(qgis_symbol, QgsLegendPatchShape):
                        style.addLegendPatchShape(unique_name, qgis_symbol, True)

                if tags:
                    if isinstance(qgis_symbol, QgsSymbol):
                        assert style.tagSymbol(QgsStyle.SymbolEntity, unique_name, tags)
                    elif isinstance(qgis_symbol, QgsColorRamp):
                        assert style.tagSymbol(QgsStyle.ColorrampEntity, unique_name, tags)
                    elif isinstance(qgis_symbol, QgsTextFormat) and hasattr(QgsStyle, 'TextFormatEntity'):
                        assert style.tagSymbol(QgsStyle.TextFormatEntity, unique_name, tags)
                    elif isinstance(qgis_symbol, QgsPalLayerSettings) and hasattr(QgsStyle, 'LabelSettingsEntity'):
                        assert style.tagSymbol(QgsStyle.LabelSettingsEntity, unique_name, tags)
                    elif Qgis.QGIS_VERSION_INT >= 31300:
                        if isinstance(qgis_symbol, QgsLegendPatchShape):
                            assert style.tagSymbol(QgsStyle.LegendPatchShapeEntity, unique_name, tags)

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
            elif symbol_type == Extractor.TEXT_SYMBOLS:
                results[self.TEXT_FORMAT_COUNT] = len(raw_symbols)
                results[self.UNREADABLE_TEXT_FORMATS] = unreadable
            elif symbol_type in (Extractor.MAPLEX_LABELS, Extractor.LABELS):
                results[self.LABEL_SETTINGS_COUNT] += len(raw_symbols)
                results[self.UNREADABLE_LABEL_SETTINGS] += unreadable
            elif symbol_type == Extractor.LINE_PATCHES:
                results[self.LINE_PATCH_COUNT] = len(raw_symbols)
                results[self.UNREADABLE_LINE_PATCHES] = unreadable
            elif symbol_type == Extractor.AREA_PATCHES:
                results[self.AREA_PATCH_COUNT] = len(raw_symbols)
                results[self.UNREADABLE_AREA_PATCHES] = unreadable

        style.exportXml(output_file)
        results[self.OUTPUT] = output_file
        results[self.REPORT] = dest
        return results

    # pylint: enable=missing-docstring,unused-argument
