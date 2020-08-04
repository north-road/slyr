# -*- coding: utf-8 -*-

# /***************************************************************************
# context.py
# ----------
# Date                 : September 2019
# copyright            : (C) 2019 by Nyall Dawson, SMEC
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
SLYR QGIS Processing algorithms
"""

import os
from io import BytesIO
from qgis.core import (Qgis,
                       QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingOutputNumber,
                       QgsProcessingParameterDefinition,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingOutputString,
                       QgsProcessingException,
                       QgsStyle,
                       QgsFeature,
                       QgsFields,
                       QgsField,
                       QgsColorRamp,
                       QgsSymbol)

HAS_BOOLEAN_OUTPUT = False
try:
    from qgis.core import QgsProcessingOutputBoolean

    HAS_BOOLEAN_OUTPUT = True
except ImportError:
    pass

try:
    from qgis.core import QgsLegendPatchShape
except ImportError:
    pass

from qgis.PyQt.QtCore import QVariant

from slyr_community.bintools.extractor import Extractor, MissingBinaryException
from slyr_community.parser.stream import Stream
from slyr_community.parser.exceptions import (UnreadableSymbolException,
                                              InvalidColorException,
                                              UnsupportedVersionException,
                                              NotImplementedException,
                                              UnknownClsidException,
                                              UnreadablePictureException)
from slyr_community.converters.context import Context
from slyr_community.converters.symbols import SymbolConverter
from slyr_community.converters.color import ColorConverter


class SlyrAlgorithm(QgsProcessingAlgorithm):

    def canExecute(self):
        return True, None


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

    def createInstance(self):  # pylint: disable=missing-docstring
        return StyleToQgisXml()

    def name(self):  # pylint: disable=missing-docstring
        return 'styletoqgisxml'

    def displayName(self):  # pylint: disable=missing-docstring
        return 'Convert ESRI style to QGIS style XML'

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

    def processAlgorithm(self,  # pylint:disable=missing-docstring,too-many-locals,too-many-statements,too-many-branches
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
                raise QgsProcessingException(
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

                if symbol_type in (
                Extractor.AREA_PATCHES, Extractor.LINE_PATCHES, Extractor.TEXT_SYMBOLS, Extractor.MAPLEX_LABELS,
                Extractor.LABELS):
                    if symbol_type == Extractor.AREA_PATCHES:
                        type_string = 'area patches'
                    elif symbol_type == Extractor.LINE_PATCHES:
                        type_string = 'line patches'
                    elif symbol_type == Extractor.TEXT_SYMBOLS:
                        type_string = 'text symbols'
                    elif symbol_type == Extractor.MAPLEX_LABELS:
                        type_string = 'maplex labels'
                    elif symbol_type == Extractor.LABELS:
                        type_string = 'labels'
                    else:
                        type_string = ''

                    feedback.reportError(
                        'Converting {} is available in the licensed version of SLYR only - please see https://north-road.com/slyr/ for details'.format(
                            type_string))
                    unreadable += 1
                    continue

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
                        f = QgsFeature()
                        f.setAttributes([name, msg])
                        sink.addFeature(f)

                context = Context()
                context.symbol_name = unique_name
                context.style_folder, _ = os.path.split(output_file)
                context.unsupported_object_callback = unsupported_object_callback

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

                if tags:
                    if isinstance(qgis_symbol, QgsSymbol):
                        assert style.tagSymbol(QgsStyle.SymbolEntity, unique_name, tags)
                    elif isinstance(qgis_symbol, QgsColorRamp):
                        assert style.tagSymbol(QgsStyle.ColorrampEntity, unique_name, tags)

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


class StyleToGpl(SlyrAlgorithm):
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

    def processAlgorithm(self,  # pylint: disable=missing-docstring,too-many-locals,too-many-statements
                         parameters,
                         context,
                         feedback):
        input_file = self.parameterAsString(parameters, self.INPUT, context)
        output_file = self.parameterAsFileOutput(parameters, self.OUTPUT, context)

        results = {}
        colors = []

        _, file_name = os.path.split(input_file)
        file_name, _ = os.path.splitext(file_name)

        feedback.pushInfo('Importing colors from {}'.format(input_file))

        try:
            raw_colors = Extractor.extract_styles(input_file, Extractor.COLORS)
        except MissingBinaryException:
            raise QgsProcessingException('The MDB tools "mdb-export" utility is required to convert .style databases. Please setup a path to the MDB tools utility in the SLYR options panel.')

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
                feedback.reportError('Error reading color {}'.format(name), False)
                unreadable += 1
                continue

            qcolor = ColorConverter.color_to_qcolor(color)
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


class StyleFromLyr(SlyrAlgorithm):
    """
    Converts .style databases to GPL color palette files
    """

    LAYER = 'LAYER'
    LYR_FILE = 'LYR_FILE'

    def createInstance(self):  # pylint: disable=missing-docstring
        return StyleFromLyr()

    def name(self):  # pylint: disable=missing-docstring
        return 'stylefromlyr'

    def displayName(self):  # pylint: disable=missing-docstring
        return 'Set style from LYR file'

    def shortDescription(self):  # pylint: disable=missing-docstring
        return 'Sets a layer\'s settings and symbology from an ESRI LYR file'

    def group(self):  # pylint: disable=missing-docstring
        return 'LYR datasets'

    def groupId(self):  # pylint: disable=missing-docstring
        return 'lyr'

    def shortHelpString(self):  # pylint: disable=missing-docstring
        return "Sets a layer\'s settings and symbology from an ESRI LYR file"

    def initAlgorithm(self, config=None):  # pylint: disable=missing-docstring,unused-argument
        self.addParameter(QgsProcessingParameterVectorLayer(
            self.LAYER, 'Destination layer'))

        self.addParameter(QgsProcessingParameterFile(
            self.LYR_FILE, 'LYR file', extension='lyr'))

    def flags(self):  # pylint: disable=missing-docstring
        return super().flags() | QgsProcessingAlgorithm.FlagNoThreading

    def processAlgorithm(self,  # pylint: disable=missing-docstring,too-many-locals,too-many-statements
                         parameters,  # pylint: disable=unused-argument
                         context,  # pylint: disable=unused-argument
                         feedback):  # pylint: disable=unused-argument
        raise QgsProcessingException(
            'This algorithm is available in the licensed version of SLYR only - please see https://north-road.com/slyr/ for details')


class LyrToQlr(SlyrAlgorithm):
    """
    Converts .lyr to QLR
    """

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    CONVERTED = 'CONVERTED'
    ERROR = 'ERROR'

    def createInstance(self):  # pylint: disable=missing-docstring
        return LyrToQlr()

    def name(self):  # pylint: disable=missing-docstring
        return 'lyrtoqlr'

    def displayName(self):  # pylint: disable=missing-docstring
        return 'Convert LYR to QLR'

    def shortDescription(self):  # pylint: disable=missing-docstring
        return 'Converts an ESRI LYR file to a QGIS QLR file'

    def group(self):  # pylint: disable=missing-docstring
        return 'LYR datasets'

    def groupId(self):  # pylint: disable=missing-docstring
        return 'lyr'

    def shortHelpString(self):  # pylint: disable=missing-docstring
        return "Converts an ESRI LYR file to a QGIS QLR file"

    def initAlgorithm(self, config=None):  # pylint: disable=missing-docstring,unused-argument
        self.addParameter(QgsProcessingParameterFile(
            self.INPUT, 'Input LYR file', extension='lyr'))

        self.addParameter(QgsProcessingParameterFileDestination(
            self.OUTPUT, 'Destination QLR file', fileFilter='QLR files (*.qlr)'))

        if HAS_BOOLEAN_OUTPUT:
            self.addOutput(QgsProcessingOutputBoolean(self.CONVERTED, 'Converted'))
        self.addOutput(QgsProcessingOutputString(self.ERROR, 'Error message'))

    def processAlgorithm(self,  # pylint: disable=missing-docstring,too-many-locals,too-many-statements
                         parameters,
                         context,
                         feedback):
        raise QgsProcessingException(
            'This algorithm is available in the licensed version of SLYR only - please see https://north-road.com/slyr/ for details')


class LyrToQml(SlyrAlgorithm):
    """
    Converts .lyr to QML
    """

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    CONVERTED = 'CONVERTED'
    ERROR = 'ERROR'

    def createInstance(self):  # pylint: disable=missing-docstring
        return LyrToQml()

    def name(self):  # pylint: disable=missing-docstring
        return 'lyrtoqml'

    def displayName(self):  # pylint: disable=missing-docstring
        return 'Convert LYR to QML'

    def shortDescription(self):  # pylint: disable=missing-docstring
        return 'Converts an ESRI LYR file to a QGIS QML file (or files)'

    def group(self):  # pylint: disable=missing-docstring
        return 'LYR datasets'

    def groupId(self):  # pylint: disable=missing-docstring
        return 'lyr'

    def shortHelpString(self):  # pylint: disable=missing-docstring
        return "Converts an ESRI LYR file to a QGIS QML file. If multiple layers are present in the LYR file, each will "

    "be converted to an individual QML file."

    def initAlgorithm(self, config=None):  # pylint: disable=missing-docstring,unused-argument
        self.addParameter(QgsProcessingParameterFile(
            self.INPUT, 'Input LYR file', extension='lyr'))

        self.addParameter(QgsProcessingParameterFileDestination(
            self.OUTPUT, 'Destination QML file', fileFilter='QML files (*.qml)'))

        if HAS_BOOLEAN_OUTPUT:
            self.addOutput(QgsProcessingOutputBoolean(self.CONVERTED, 'Converted'))
        self.addOutput(QgsProcessingOutputString(self.ERROR, 'Error message'))

    def processAlgorithm(self,  # pylint: disable=missing-docstring,too-many-locals,too-many-statements
                         parameters,
                         context,
                         feedback):
        raise QgsProcessingException(
            'This algorithm is available in the licensed version of SLYR only - please see https://north-road.com/slyr/ for details')


class AvlToQml(SlyrAlgorithm):
    """
    Converts .avl to QML
    """

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    CONVERTED = 'CONVERTED'
    ERROR = 'ERROR'

    def createInstance(self):  # pylint: disable=missing-docstring
        return AvlToQml()

    def name(self):  # pylint: disable=missing-docstring
        return 'avltoqml'

    def displayName(self):  # pylint: disable=missing-docstring
        return 'Convert AVL to QML'

    def shortDescription(self):  # pylint: disable=missing-docstring
        return 'Converts an ESRI ArcInfo AVL file to a QGIS QML file'

    def group(self):  # pylint: disable=missing-docstring
        return 'AVL styles'

    def groupId(self):  # pylint: disable=missing-docstring
        return 'avl'

    def shortHelpString(self):  # pylint: disable=missing-docstring
        return "Converts an ESRI ArcInfo AVL file to a QGIS QML file."

    def initAlgorithm(self, config=None):  # pylint: disable=missing-docstring,unused-argument
        self.addParameter(QgsProcessingParameterFile(
            self.INPUT, 'Input AVL file', extension='avl'))

        self.addParameter(QgsProcessingParameterFileDestination(
            self.OUTPUT, 'Destination QML file', fileFilter='QML files (*.qml)'))

        if HAS_BOOLEAN_OUTPUT:
            self.addOutput(QgsProcessingOutputBoolean(self.CONVERTED, 'Converted'))
        self.addOutput(QgsProcessingOutputString(self.ERROR, 'Error message'))

    def processAlgorithm(self,  # pylint: disable=missing-docstring,too-many-locals,too-many-statements
                         parameters,
                         context,
                         feedback):
        raise QgsProcessingException(
            'This algorithm is available in the licensed version of SLYR only - please see https://north-road.com/slyr/ for details')


class LyrToStyleXml(SlyrAlgorithm):
    """
    Converts .lyr to QGIS style XML
    """

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'

    def createInstance(self):  # pylint: disable=missing-docstring
        return LyrToStyleXml()

    def name(self):  # pylint: disable=missing-docstring
        return 'lyrtostylexml'

    def displayName(self):  # pylint: disable=missing-docstring
        return 'Convert LYR to QGIS style XML'

    def shortDescription(self):  # pylint: disable=missing-docstring
        return 'Converts an ESRI LYR file to a QGIS style XML file'

    def group(self):  # pylint: disable=missing-docstring
        return 'LYR datasets'

    def groupId(self):  # pylint: disable=missing-docstring
        return 'lyr'

    def shortHelpString(self):  # pylint: disable=missing-docstring
        return "Converts an ESRI LYR file to a QGIS style XML file"

    def initAlgorithm(self, config=None):  # pylint: disable=missing-docstring,unused-argument
        self.addParameter(QgsProcessingParameterFile(
            self.INPUT, 'Input LYR file', extension='lyr'))

        self.addParameter(QgsProcessingParameterFileDestination(
            self.OUTPUT, 'Destination style XML file', fileFilter='XML files (*.xml)'))

    def processAlgorithm(self,  # pylint: disable=missing-docstring,too-many-locals,too-many-statements
                         parameters,  # pylint: disable=unused-argument
                         context,  # pylint: disable=unused-argument
                         feedback):  # pylint: disable=unused-argument

        raise QgsProcessingException(
            'This algorithm is available in the licensed version of SLYR only - please see https://north-road.com/slyr/ for details')


class AddLayersFromMxd(SlyrAlgorithm):
    """
    Adds layers from an MXD document to the current project
    """

    INPUT = 'INPUT'

    def __init__(self):
        super().__init__()
        self.obj = None
        self.input_file = ''

    def createInstance(self):  # pylint: disable=missing-docstring
        return AddLayersFromMxd()

    def name(self):  # pylint: disable=missing-docstring
        return 'addlayersfrommxd'

    def displayName(self):  # pylint: disable=missing-docstring
        return 'Add layers from MXD to project'

    def shortDescription(self):  # pylint: disable=missing-docstring
        return 'Adds layers from an MXD document to the current project, respecting their original symbology.'

    def group(self):  # pylint: disable=missing-docstring
        return 'MXD documents'

    def groupId(self):  # pylint: disable=missing-docstring
        return 'mxd'

    def shortHelpString(self):  # pylint: disable=missing-docstring
        return 'Adds layers from an MXD document to the current project, respecting their original symbology.'

    def initAlgorithm(self, config=None):  # pylint: disable=missing-docstring,unused-argument
        self.addParameter(QgsProcessingParameterFile(
            self.INPUT, 'Input MXD file', extension='mxd'))

    def processAlgorithm(self,  # pylint: disable=missing-docstring,too-many-locals,too-many-statements
                         parameters,  # pylint: disable=unused-argument
                         context,  # pylint: disable=unused-argument
                         feedback):  # pylint: disable=unused-argument
        raise QgsProcessingException(
            'This algorithm is available in the licensed version of SLYR only - please see https://north-road.com/slyr/ for details')


class ExtractPrintLayoutsFromMxd(SlyrAlgorithm):
    """
    Extracts print layouts from an MXD document and adds to the current project
    """

    INPUT = 'INPUT'

    def createInstance(self):  # pylint: disable=missing-docstring
        return ExtractPrintLayoutsFromMxd()

    def name(self):  # pylint: disable=missing-docstring
        return 'extractlayoutfrommxd'

    def displayName(self):  # pylint: disable=missing-docstring
        return 'Extract print layouts from MXD'

    def shortDescription(self):  # pylint: disable=missing-docstring
        return 'Extracts print layouts from an MXD document and adds them to the current project.'

    def group(self):  # pylint: disable=missing-docstring
        return 'MXD documents'

    def groupId(self):  # pylint: disable=missing-docstring
        return 'mxd'

    def shortHelpString(self):  # pylint: disable=missing-docstring
        return 'Extracts print layouts from an MXD document and adds them to the current project.'

    def initAlgorithm(self, config=None):  # pylint: disable=missing-docstring,unused-argument
        self.addParameter(QgsProcessingParameterFile(
            self.INPUT, 'Input MXD file', extension='mxd'))

    def processAlgorithm(self,  # pylint: disable=missing-docstring,too-many-locals,too-many-statements
                         parameters,  # pylint: disable=unused-argument
                         context,  # pylint: disable=unused-argument
                         feedback):  # pylint: disable=unused-argument
        raise QgsProcessingException(
            'This algorithm is available in the licensed version of SLYR only - please see https://north-road.com/slyr/ for details')


class ConvertMxdToQgs(SlyrAlgorithm):
    """
    Converts an MXD document to a QGS project file
    """

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    IGNORE_ONLINE = 'IGNORE_ONLINE'

    def createInstance(self):  # pylint: disable=missing-docstring
        return ConvertMxdToQgs()

    def name(self):  # pylint: disable=missing-docstring
        return 'convertmxdtoqgs'

    def displayName(self):  # pylint: disable=missing-docstring
        return 'Convert MXD/MXT to QGS'

    def shortDescription(self):  # pylint: disable=missing-docstring
        return 'Converts an MXD or MXT document file to a QGIS project file.'

    def group(self):  # pylint: disable=missing-docstring
        return 'MXD documents'

    def groupId(self):  # pylint: disable=missing-docstring
        return 'mxd'

    def shortHelpString(self):  # pylint: disable=missing-docstring
        return 'Converts an MXD or MXT document file to a QGIS project file.'

    def initAlgorithm(self, config=None):  # pylint: disable=missing-docstring,unused-argument
        if Qgis.QGIS_VERSION_INT >= 31000:
            self.addParameter(QgsProcessingParameterFile(
                self.INPUT, 'Input MXD/MXT file', fileFilter='MXD/MXT Documents (*.mxd *.MXD *.mxt *.MXT)'))
        else:
            self.addParameter(QgsProcessingParameterFile(
                self.INPUT, 'Input MXD/MXT file', extension='mxd'))

        param_no_online = QgsProcessingParameterBoolean(self.IGNORE_ONLINE, 'Ignore online sources (debug option)',
                                                        False, True)
        param_no_online.setFlags(param_no_online.flags() | QgsProcessingParameterDefinition.FlagHidden)
        self.addParameter(param_no_online)

        self.addParameter(QgsProcessingParameterFileDestination(
            self.OUTPUT, 'Destination QGS project file', fileFilter='QGS files (*.qgs)'))

    def processAlgorithm(self,  # pylint: disable=missing-docstring,too-many-locals,too-many-statements
                         parameters,  # pylint: disable=unused-argument
                         context,  # pylint: disable=unused-argument
                         feedback):  # pylint: disable=unused-argument
        raise QgsProcessingException(
            'This algorithm is available in the licensed version of SLYR only - please see https://north-road.com/slyr/ for details')


class ExportStructureToJson(SlyrAlgorithm):
    """
    Converts an MXD document to a QGS project file
    """

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'

    def createInstance(self):  # pylint: disable=missing-docstring
        return ExportStructureToJson()

    def name(self):  # pylint: disable=missing-docstring
        return 'exporttojson'

    def displayName(self):  # pylint: disable=missing-docstring
        return 'Export document structure'

    def shortDescription(self):  # pylint: disable=missing-docstring
        return 'Exports a JSON representation of the internal structure of an MXD (or LYR) document file.'

    def group(self):  # pylint: disable=missing-docstring
        return 'MXD documents'

    def groupId(self):  # pylint: disable=missing-docstring
        return 'mxd'

    def shortHelpString(self):  # pylint: disable=missing-docstring
        return 'This algorithm exports a JSON representation of the internal structure of an ESRI MXD or LYR document file.\n\n' + \
               'It is designed for debugging purposes, allowing users to view in-depth detail about the document structure ' + \
               'and layer configuration.'

    def initAlgorithm(self, config=None):  # pylint: disable=missing-docstring,unused-argument

        if Qgis.QGIS_VERSION_INT >= 31000:
            self.addParameter(QgsProcessingParameterFile(
                self.INPUT, 'Input MXD file',
                fileFilter='ArcGIS Documents (*.mxd, *.MXD, *.lyr, *.LYR);;All files (*.*)'))
        else:
            self.addParameter(QgsProcessingParameterFile(
                self.INPUT, 'Input MXD file', extension='mxd'))

        self.addParameter(QgsProcessingParameterFileDestination(
            self.OUTPUT, 'Destination JSON file', fileFilter='JSON files (*.json *.JSON);;All files (*.*)'))

    def processAlgorithm(self,  # pylint: disable=missing-docstring,too-many-locals,too-many-statements
                         parameters,  # pylint: disable=unused-argument
                         context,  # pylint: disable=unused-argument
                         feedback):  # pylint: disable=unused-argument
        raise QgsProcessingException(
            'This algorithm is available in the licensed version of SLYR only - please see https://north-road.com/slyr/ for details')


class ConvertPmfToQgs(SlyrAlgorithm):
    """
    Converts a PMF document to a QGS project file
    """

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'

    def createInstance(self):  # pylint: disable=missing-docstring
        return ConvertPmfToQgs()

    def name(self):  # pylint: disable=missing-docstring
        return 'convertpmftoqgs'

    def displayName(self):  # pylint: disable=missing-docstring
        return 'Convert PMF to QGS'

    def shortDescription(self):  # pylint: disable=missing-docstring
        return 'Converts a PMF document file to a QGIS project file.'

    def group(self):  # pylint: disable=missing-docstring
        return 'PMF published maps'

    def groupId(self):  # pylint: disable=missing-docstring
        return 'pmf'

    def shortHelpString(self):  # pylint: disable=missing-docstring
        return 'Converts a PMF document file to a QGIS project file.'

    def initAlgorithm(self, config=None):  # pylint: disable=missing-docstring,unused-argument
        self.addParameter(QgsProcessingParameterFile(
            self.INPUT, 'Input PMF file', extension='pmf'))

        self.addParameter(QgsProcessingParameterFileDestination(
            self.OUTPUT, 'Destination QGS project file', fileFilter='QGS files (*.qgs)'))

    def processAlgorithm(self,  # pylint: disable=missing-docstring,too-many-locals,too-many-statements
                         parameters,  # pylint: disable=unused-argument
                         context,  # pylint: disable=unused-argument
                         feedback):  # pylint: disable=unused-argument
        raise QgsProcessingException(
            'This algorithm is available in the licensed version of SLYR only - please see https://north-road.com/slyr/ for details')


class ConvertSxdToQgs(SlyrAlgorithm):
    """
    Converts an SXD document to a QGS project file
    """

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'

    def createInstance(self):  # pylint: disable=missing-docstring
        return ConvertSxdToQgs()

    def name(self):  # pylint: disable=missing-docstring
        return 'convertsxdtoqgs'

    def displayName(self):  # pylint: disable=missing-docstring
        return 'Convert SXD to QGS (2D)'

    def shortDescription(self):  # pylint: disable=missing-docstring
        return 'Converts an ArcScene SXD document file to a 2D QGIS project file.'

    def group(self):  # pylint: disable=missing-docstring
        return 'SXD documents'

    def groupId(self):  # pylint: disable=missing-docstring
        return 'sxd'

    def shortHelpString(self):  # pylint: disable=missing-docstring
        return 'Converts an ArcScene SXD document file to a 2D QGIS project file.'

    def initAlgorithm(self, config=None):  # pylint: disable=missing-docstring,unused-argument
        self.addParameter(QgsProcessingParameterFile(
            self.INPUT, 'Input SXD file', extension='sxd'))

        self.addParameter(QgsProcessingParameterFileDestination(
            self.OUTPUT, 'Destination QGS project file', fileFilter='QGS files (*.qgs)'))

    def processAlgorithm(self,  # pylint: disable=missing-docstring,too-many-locals,too-many-statements
                         parameters,  # pylint: disable=unused-argument
                         context,  # pylint: disable=unused-argument
                         feedback):  # pylint: disable=unused-argument
        raise QgsProcessingException(
            'This algorithm is available in the licensed version of SLYR only - please see https://north-road.com/slyr/ for details')
