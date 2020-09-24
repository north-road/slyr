# -*- coding: utf-8 -*-

# /***************************************************************************
# browser.py
# ----------
# Date                 : September 2019
# copyright            : (C) 2019 by Nyall Dawson
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
Browser and app integrations for LYR/STYLE file integration with QGIS
"""
import html
from io import BytesIO
from functools import partial

from qgis.PyQt.QtCore import QFileInfo, QDir, QCoreApplication
from qgis.PyQt.QtWidgets import (
    QAction,
    QProgressDialog,
    QPushButton)
from qgis.PyQt.QtXml import QDomDocument

from qgis.core import (
    QgsApplication,
    Qgis,
    QgsDataItem,
    QgsErrorItem,
    QgsDataItemProvider,
    QgsMimeDataUtils,
    QgsStyle,
    QgsFeedback,
    QgsSymbol,
    QgsColorRamp,
    QgsDataProvider,
    QgsLayerItem,
    QgsMessageOutput,
    QgsCsException,
)
from qgis.gui import (
    QgsCustomDropHandler,
    QgsStyleManagerDialog,
    QgsLayoutCustomDropHandler
)
from qgis.utils import iface

from processing import execAlgorithmDialog

from slyr_community.bintools.extractor import Extractor, MissingBinaryException
from slyr_community.parser.stream import Stream
from slyr_community.parser.exceptions import (UnreadableSymbolException,
                                              UnsupportedVersionException,
                                              NotImplementedException,
                                              UnknownClsidException,
                                              UnreadablePictureException)
from slyr_community.converters.context import Context
from slyr_community.converters.symbols import SymbolConverter
from slyr_community.qgis_plugin.gui_utils import GuiUtils

USE_PROJECT_OPEN_HANDLER = False

try:
    from qgis.core import QgsLegendPatchShape  # pylint: disable=unused-import,ungrouped-imports
except ImportError:
    pass


def show_warning(short_message, title, long_message, level=Qgis.Warning, message_bar=None):
    """
    Shows a warning via the QGIS message bar
    """

    def show_details(_):
        dialog = QgsMessageOutput.createMessageOutput()
        dialog.setTitle(title)
        dialog.setMessage(long_message, QgsMessageOutput.MessageHtml)
        dialog.showMessage()

    if message_bar is None:
        message_bar = iface.messageBar()
    message_widget = message_bar.createMessage('SLYR', short_message)
    details_button = QPushButton("Details")
    details_button.clicked.connect(show_details)
    message_widget.layout().addWidget(details_button)
    return message_bar.pushWidget(message_widget, level, 0)


def open_settings(message_bar_widget=None):
    """
    Opens the settings dialog at the SLYR options page
    """
    iface.showOptionsDialog(iface.mainWindow(), currentPage='slyrOptions')
    if message_bar_widget:
        iface.messageBar().popWidget(message_bar_widget)


if USE_PROJECT_OPEN_HANDLER:
    class MxdProjectOpenHandler(QgsCustomProjectOpenHandler):  # pylint: disable=undefined-variable
        """
        Custom project open handler for MXD documents
        """

        def filters(self):  # pylint: disable=missing-function-docstring
            return ['ArcGIS MXD Documents (*.mxd *.MXD)',
                    'ArcGIS MXT Templates (*.mxt *.MXT)',
                    'ArcReader Published Map Files (*.pmf *.PMF)',
                    'ArcScene SXD Documents (*.sxd *.SXD)',
                    ]

        def handleProjectOpen(self, file):  # pylint: disable=missing-function-docstring
            return MxdDropHandler.open_mxd(file)

        def createDocumentThumbnailAfterOpen(self):  # pylint: disable=missing-function-docstring
            return True

        def icon(self):  # pylint: disable=missing-function-docstring
            return GuiUtils.get_icon('mxd.svg')


class LayoutDropHandler(QgsLayoutCustomDropHandler):
    """
    Handles pasting layout elements from ArcMap
    """

    def __init__(self, parent=None):  # pylint: disable=useless-super-delegation
        super().__init__(parent)

    def handlePaste(self,  # pylint: disable=missing-function-docstring,unused-argument
                    designer_iface,  # pylint: disable=unused-argument
                    pastePoint,  # pylint: disable=unused-argument
                    data):  # pylint: disable=unused-argument
        if 'application/x-qt-windows-mime;value="Esri Graphics List"' not in data.formats():
            return False, []

        message = '<p>Pasting page layout elements requires the licensed version of SLYR. Please see <a href="https://north-road.com/slyr/">here</a> for details.</p>'
        show_warning('Could not paste all elements', 'Paste Elements', message,
                     level=Qgis.Critical, message_bar=designer_iface.messageBar())
        return True, []


class NameDropHandler(QgsCustomDropHandler):
    """
    Handles dropping ESRI name mime data
    """

    DATA_TYPE = 'application/x-qt-windows-mime;value="ESRI Names"'

    def customUriProviderKey(self):  # pylint: disable=missing-function-docstring
        return 'esri_names'

    def canHandleMimeData(self, data):  # pylint: disable=missing-function-docstring
        return data.hasFormat(NameDropHandler.DATA_TYPE)

    def handleMimeDataV2(self, data):  # pylint: disable=missing-function-docstring
        if data.hasFormat(NameDropHandler.DATA_TYPE):
            message = '<p>This functionality requires the licensed version of SLYR. Please see <a href="https://north-road.com/slyr/">here</a> for details.</p>'
            show_warning('Could not handle item drop', '', message,
                         level=Qgis.Critical, message_bar=iface.messageBar())
            return True
        return False


class StyleDropHandler(QgsCustomDropHandler):
    """
    .style file drop handler
    """

    def handleFileDrop(self, file):  # pylint: disable=missing-docstring
        if not file.lower().endswith('.style'):
            return False
        return self.open_style(file)

    @staticmethod
    def open_style(input_file):  # pylint: disable=too-many-locals,too-many-branches,too-many-statements
        """
        Opens a .style file
        """

        if not Extractor.is_mdb_tools_binary_available():
            message_bar = iface.messageBar()
            widget = message_bar.createMessage('SLYR', "MDB Tools utility not found")
            settings_button = QPushButton("Configure…", pressed=partial(open_settings, widget))
            widget.layout().addWidget(settings_button)
            message_bar.pushWidget(widget, Qgis.Critical)
            return True

        style = QgsStyle()
        style.createMemoryDatabase()

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

        feedback = QgsFeedback()

        progress_dialog = QProgressDialog("Loading style database…", "Abort", 0, 100, None)
        progress_dialog.setWindowTitle("Loading Style")

        def progress_changed(progress):
            """
            Handles feedback to progress dialog bridge
            """
            progress_dialog.setValue(progress)
            iters = 0
            while QCoreApplication.hasPendingEvents() and iters < 100:
                QCoreApplication.processEvents()
                iters += 1

        feedback.progressChanged.connect(progress_changed)

        def cancel():
            """
            Slot to cancel the import
            """
            feedback.cancel()

        progress_dialog.canceled.connect(cancel)
        unreadable = []
        warnings = set()
        errors = set()

        types_to_extract = [Extractor.FILL_SYMBOLS, Extractor.LINE_SYMBOLS, Extractor.MARKER_SYMBOLS,
                            Extractor.COLOR_RAMPS,
                            Extractor.TEXT_SYMBOLS, Extractor.LABELS, Extractor.MAPLEX_LABELS, Extractor.AREA_PATCHES,
                            Extractor.LINE_PATCHES]

        type_percent = 100 / len(types_to_extract)

        for type_index, symbol_type in enumerate(types_to_extract):

            try:
                raw_symbols = Extractor.extract_styles(input_file, symbol_type)
            except MissingBinaryException:
                show_warning('MDB Tools utility not found', 'Convert style',
                             'The MDB tools "mdb-export" utility is required to convert .style databases. Please setup a path to the MDB tools utility in the SLYR options panel.',
                             level=Qgis.Critical)
                progress_dialog.deleteLater()
                return True

            if feedback.isCanceled():
                break

            for index, raw_symbol in enumerate(raw_symbols):
                feedback.setProgress(index / len(raw_symbols) * type_percent + type_percent * type_index)
                if feedback.isCanceled():
                    break
                name = raw_symbol[Extractor.NAME]
                tags = raw_symbol[Extractor.TAGS].split(';')

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

                    unreadable.append('<b>{}</b>: {} conversion requires a licensed version of the SLYR plugin'.format(
                        html.escape(name), type_string))
                    continue

                unique_name = make_name_unique(name)

                handle = BytesIO(raw_symbol[Extractor.BLOB])
                stream = Stream(handle)
                stream.allow_shortcuts = False

                try:
                    symbol = stream.read_object()
                except UnreadableSymbolException as e:
                    e = 'Unreadable object: {}'.format(e)
                    unreadable.append('<b>{}</b>: {}'.format(html.escape(name), html.escape(str(e))))
                    continue
                except NotImplementedException as e:
                    unreadable.append('<b>{}</b>: {}'.format(html.escape(name), html.escape(str(e))))
                    continue
                except UnsupportedVersionException as e:
                    e = 'Unsupported version: {}'.format(e)
                    unreadable.append('<b>{}</b>: {}'.format(html.escape(name), html.escape(str(e))))
                    continue
                except UnknownClsidException as e:
                    unreadable.append('<b>{}</b>: {}'.format(html.escape(name), html.escape(str(e))))
                    continue
                except UnreadablePictureException as e:
                    unreadable.append('<b>{}</b>: {}'.format(html.escape(name), html.escape(str(e))))
                    continue

                context = Context()
                context.symbol_name = unique_name

                def unsupported_object_callback(msg, level=Context.WARNING):
                    if level == Context.WARNING:
                        warnings.add('<b>{}</b>: {}'.format(html.escape(unique_name),  # pylint: disable=cell-var-from-loop
                                                            html.escape(msg)))
                    elif level == Context.CRITICAL:
                        errors.add('<b>{}</b>: {}'.format(html.escape(unique_name),  # pylint: disable=cell-var-from-loop
                                                          html.escape(msg)))

                context.unsupported_object_callback = unsupported_object_callback
                # context.style_folder, _ = os.path.split(output_file)

                try:
                    qgis_symbol = SymbolConverter.Symbol_to_QgsSymbol(symbol, context)
                except NotImplementedException as e:
                    unreadable.append('<b>{}</b>: {}'.format(html.escape(name), html.escape(str(e))))
                    continue
                except UnreadablePictureException as e:
                    unreadable.append('<b>{}</b>: {}'.format(html.escape(name), html.escape(str(e))))
                    continue

                if isinstance(qgis_symbol, QgsSymbol):
                    # self.check_for_missing_fonts(qgis_symbol, feedback)
                    style.addSymbol(unique_name, qgis_symbol, True)
                elif isinstance(qgis_symbol, QgsColorRamp):
                    style.addColorRamp(unique_name, qgis_symbol, True)

                if tags:
                    if isinstance(qgis_symbol, QgsSymbol):
                        assert style.tagSymbol(QgsStyle.SymbolEntity, unique_name, tags)
                    elif isinstance(qgis_symbol, QgsColorRamp):
                        assert style.tagSymbol(QgsStyle.ColorrampEntity, unique_name, tags)
        progress_dialog.deleteLater()
        if feedback.isCanceled():
            return True

        if errors or unreadable or warnings:
            message = ''
            if unreadable:
                message = '<p>The following symbols could not be converted:</p>'
                message += '<ul>'
                for w in unreadable:
                    message += '<li>{}</li>'.format(w.replace('\n', '<br>'))
                message += '</ul>'

            if errors:
                message += '<p>The following errors were generated while converting symbols:</p>'
                message += '<ul>'
                for w in errors:
                    message += '<li>{}</li>'.format(w.replace('\n', '<br>'))
                message += '</ul>'

            if warnings:
                message += '<p>The following warnings were generated while converting symbols:</p>'
                message += '<ul>'
                for w in warnings:
                    message += '<li>{}</li>'.format(w.replace('\n', '<br>'))
                message += '</ul>'

            show_warning('style could not be completely converted', 'Convert style', message,
                         level=Qgis.Critical if (unreadable or errors) else Qgis.Warning)

        if Qgis.QGIS_VERSION_INT >= 30800:
            dlg = QgsStyleManagerDialog(style, readOnly=True)
            dlg.setFavoritesGroupVisible(False)
            dlg.setSmartGroupsVisible(False)
            fi = QFileInfo(input_file)
            dlg.setBaseStyleName(fi.baseName())
        else:
            dlg = QgsStyleManagerDialog(style)
        dlg.exec_()
        return True

    def customUriProviderKey(self):  # pylint: disable=missing-docstring
        return 'esri_style'

    def handleCustomUriDrop(self, uri):  # pylint: disable=missing-docstring
        path = uri.uri
        self.open_style(path)


class LyrDropHandler(QgsCustomDropHandler):
    """
    .lyr file drop handler
    """

    def handleFileDrop(self, file):  # pylint: disable=missing-docstring
        if not file.lower().endswith('.lyr'):
            return False
        self.open_lyr(file)

        return True

    def canHandleMimeData(self, data):  # pylint: disable=missing-function-docstring
        return data.hasFormat('application/x-qt-windows-mime;value="ESRI Layers"')

    def handleMimeDataV2(self, data):  # pylint: disable=missing-function-docstring
        if data.hasFormat('application/x-qt-windows-mime;value="ESRI Layers"'):
            message = '<p>This functionality requires the licensed version of SLYR. Please see <a href="https://north-road.com/slyr/">here</a> for details.</p>'
            show_warning('Could not handle item drop', '', message,
                         level=Qgis.Critical, message_bar=iface.messageBar())
            return True

        return False

    @staticmethod
    def open_lyr_stream(stream, input_file=''):  # pylint: disable=unused-argument
        """
        Opens a lyr file from a binary object
        """
        message = '<p>This functionality requires the licensed version of SLYR. Please see <a href="https://north-road.com/slyr/">here</a> for details.</p>'
        show_warning('Licensed version required', 'Convert LYR', message,
                     level=Qgis.Critical, message_bar=iface.messageBar())
        return True

    @staticmethod
    def open_lyr(input_file):
        """
        Opens a LYR file in the current project
        """
        with open(input_file, 'rb') as f:
            stream = Stream(f, False, force_layer=True)
            return LyrDropHandler.open_lyr_stream(stream, input_file)

    def customUriProviderKey(self):  # pylint: disable=missing-docstring
        return 'esri_lyr'

    def handleCustomUriDrop(self, uri):  # pylint: disable=missing-docstring
        path = uri.uri
        self.open_lyr(path)


blocker = None


class MxdDropHandler(QgsCustomDropHandler):
    """
    .mxd/.pmf/.sxd/.3dd file drop handler
    """

    def handleFileDrop(self, file):  # pylint: disable=missing-docstring
        if not (file.lower().endswith('.mxd') or file.lower().endswith('.sxd') or file.lower().endswith(
                '.pmf') or file.lower().endswith('.3dd') or file.lower().endswith('.mxt')):
            return False
        return self.open_mxd(file)

    @staticmethod
    def open_mxd(input_file, use_warnings=True):  # pylint: disable=unused-argument
        """
        Opens an MXD file in the current project
        """
        message = '<p>This functionality requires the licensed version of SLYR. Please see <a href="https://north-road.com/slyr/">here</a> for details.</p>'
        show_warning('Licensed version required', 'Convert MXD', message,
                     level=Qgis.Critical, message_bar=iface.messageBar())
        return True

    def customUriProviderKey(self):  # pylint: disable=missing-docstring
        return 'esri_mxd'

    def handleCustomUriDrop(self, uri):  # pylint: disable=missing-docstring
        path = uri.uri
        self.open_mxd(path)


class DatDropHandler(QgsCustomDropHandler):
    """
    .dat bookmarks file drop handler
    """

    @staticmethod
    def is_bookmark_dat(file):
        """
        Tests whether a file is an ESRI bookmark dat file
        """
        if not file.lower().endswith('.dat'):
            return False
        # check for file signature
        with open(file, 'rb') as f:
            try:
                if not f.read(4) == b'\xd0\xcf\x11\xe0':
                    return False
            except Exception:  # pylint: disable=broad-except
                return False

        return True

    def handleFileDrop(self, file):  # pylint: disable=missing-docstring
        if not DatDropHandler.is_bookmark_dat(file):
            return False

        self.open_dat(file)
        return True

    @staticmethod
    def get_bookmarks(input_file):  # pylint: disable=unused-argument
        """
        Returns a list of bookmarks from a file
        """
        return []

    @staticmethod
    def open_dat(input_file):  # pylint: disable=unused-argument
        """
        Opens an dat bookmark file in the current project
        """
        message = '<p>This functionality requires the licensed version of SLYR. Please see <a href="https://north-road.com/slyr/">here</a> for details.</p>'
        show_warning('Licensed version required', 'Convert Bookmarks', message,
                     level=Qgis.Critical, message_bar=iface.messageBar())

        return True

    def customUriProviderKey(self):  # pylint: disable=missing-docstring
        return 'esri_dat'

    def handleCustomUriDrop(self, uri):  # pylint: disable=missing-docstring
        path = uri.uri
        self.open_dat(path)


class EsriStyleItem(QgsDataItem):
    """
    Data item for .style files
    """

    def __init__(self, parent, name, path):
        super().__init__(QgsDataItem.Custom, parent, name, path)
        self.setState(QgsDataItem.Populated)  # no children
        self.setToolTip(QDir.toNativeSeparators(path))

    def hasDragEnabled(self):  # pylint: disable=missing-docstring
        return True

    def handleDoubleClick(self):  # pylint: disable=missing-docstring
        self.open_style()
        return True

    def icon(self):  # pylint: disable=missing-docstring
        return GuiUtils.get_icon('icon.svg')

    def mimeUri(self):  # pylint: disable=missing-docstring
        u = QgsMimeDataUtils.Uri()
        u.layerType = "custom"
        u.providerKey = "esri_style"
        u.name = self.name()
        u.uri = self.path()
        return u

    def open_style(self):
        """
        Opens a STYLE file in the current project
        """
        StyleDropHandler.open_style(self.path())

    def convert_style(self):
        """
        Executes the style to xml conversion algorithm
        """
        execAlgorithmDialog('slyr:styletoqgisxml', {'INPUT': self.path()})

    def actions(self, parent):  # pylint: disable=missing-docstring
        open_action = QAction(QCoreApplication.translate('SLYR', '&Open Style…'), parent)
        open_action.triggered.connect(self.open_style)
        convert_action = QAction(QCoreApplication.translate('SLYR', '&Convert Style…'), parent)
        convert_action.triggered.connect(self.convert_style)
        return [open_action, convert_action]


class EsriLyrItem(QgsDataItem):
    """
    Data item for .lyr files
    """

    def __init__(self, parent, name, path, lyr_object=None, layer_path=''):
        super().__init__(QgsDataItem.Custom, parent, name, path)
        self.setCapabilities(QgsDataItem.Fertile | QgsDataItem.Collapse)
        self.layer_path = layer_path or path
        self.object = lyr_object
        if path:
            self.setIcon(GuiUtils.get_icon('icon.svg'))
        else:
            self.setIcon(QgsLayerItem.iconDefault())

        if self.object:
            self.setState(QgsDataItem.Populated)
        self.setToolTip(QDir.toNativeSeparators(path) if not lyr_object else lyr_object.name)
        self.child_items = []

    def hasDragEnabled(self):  # pylint: disable=missing-docstring
        return True

    def handleDoubleClick(self):  # pylint: disable=missing-docstring
        if self.path():
            self.open_lyr()
        else:
            self.open_object()
        return True

    def add_children(self):
        """
        Adds a child data item from the LYR
        """
        for c in self.object.children:
            self.addChildItem(EsriLyrItem(self, c.name, '', c, self.layer_path))

    def createChildren(self):  # pylint: disable=missing-function-docstring
        # Runs in a thread!
        self.setState(QgsDataItem.Populating)

        def add_layer(layer):  # pylint: disable=unused-variable
            self.child_items.append(EsriLyrItem(self, layer.name, '', layer, self.path()))

        def add_group(group):  # pylint: disable=unused-variable
            self.child_items.append(EsriLyrItem(self, group.name, '', group, self.path()))

        self.setState(QgsDataItem.Populated)
        return self.child_items

    def mimeUri(self):  # pylint: disable=missing-docstring
        u = QgsMimeDataUtils.Uri()
        u.layerType = "custom"
        u.providerKey = "esri_lyr"
        u.name = self.name()
        u.uri = self.layer_path
        return u

    def open_lyr(self):
        """
        Handles opening .lyr files
        """
        LyrDropHandler.open_lyr(self.path())

    def open_object(self):
        """
        Opens a LYR or sublayer from a LYR file
        """

    def extract_symbols(self):
        """
        Extract symbols from a lyr file
        """
        message = '<p>This functionality requires the licensed version of SLYR. Please see <a href="https://north-road.com/slyr/">here</a> for details.</p>'
        show_warning('Licensed version required', 'Convert LYR', message,
                     level=Qgis.Critical, message_bar=iface.messageBar())
        return True

    def save_as_qlr(self):
        """
        Saves the lyr as a QLR file
        """
        message = '<p>This functionality requires the licensed version of SLYR. Please see <a href="https://north-road.com/slyr/">here</a> for details.</p>'
        show_warning('Licensed version required', 'Convert LYR', message,
                     level=Qgis.Critical, message_bar=iface.messageBar())

    def save_as_qml(self):
        """
        Saves the lyr as a QML file
        """
        message = '<p>This functionality requires the licensed version of SLYR. Please see <a href="https://north-road.com/slyr/">here</a> for details.</p>'
        show_warning('Licensed version required', 'Convert LYR', message,
                     level=Qgis.Critical, message_bar=iface.messageBar())

    def actions(self, parent):  # pylint: disable=missing-docstring
        save_as_qlr_action = QAction(QCoreApplication.translate('SLYR', 'Save as &QLR…'), parent)
        save_as_qlr_action.triggered.connect(self.save_as_qlr)
        if self.path():
            open_action = QAction(QCoreApplication.translate('SLYR', '&Add Layer(s)'), parent)
            open_action.triggered.connect(self.open_lyr)
            save_as_qml_action = QAction(QCoreApplication.translate('SLYR', 'Save as QML…'), parent)
            save_as_qml_action.triggered.connect(self.save_as_qml)
            extract_symbols_action = QAction(QCoreApplication.translate('SLYR', '&Extract Symbols…'), parent)
            extract_symbols_action.triggered.connect(self.extract_symbols)
            return [open_action, save_as_qlr_action, save_as_qml_action, extract_symbols_action]
        else:
            open_action = QAction(QCoreApplication.translate('SLYR', '&Add Layer'), parent)
            open_action.triggered.connect(self.open_object)
            save_as_qml_action = QAction(QCoreApplication.translate('SLYR', 'Save Layer as QML…'), parent)
            save_as_qml_action.triggered.connect(self.save_as_qml)
            return [open_action, save_as_qlr_action, save_as_qml_action]


class EsriMxdItem(QgsDataItem):
    """
    Data item for .mxd files
    """

    def __init__(self, parent, name, path):
        super().__init__(QgsDataItem.Custom, parent, name, path)
        self.setState(QgsDataItem.Populated)  # no children
        self.setToolTip(QDir.toNativeSeparators(path))

    def hasDragEnabled(self):  # pylint: disable=missing-docstring
        return True

    def handleDoubleClick(self):  # pylint: disable=missing-docstring
        self.open_mxd()
        return True

    def icon(self):  # pylint: disable=missing-docstring
        return GuiUtils.get_icon('mxd.svg')

    def mimeUri(self):  # pylint: disable=missing-docstring
        u = QgsMimeDataUtils.Uri()
        u.layerType = "custom"
        u.providerKey = "esri_mxd"
        u.name = self.name()
        u.uri = self.path()
        return u

    def open_mxd(self):
        """
        Handles opening .mxd files
        """
        MxdDropHandler.open_mxd(self.path())

    def actions(self, parent):  # pylint: disable=missing-docstring
        if self.path().lower().endswith('mxd'):
            action_text = QCoreApplication.translate('SLYR', '&Open MXD…')
        elif self.path().lower().endswith('mxt'):
            action_text = QCoreApplication.translate('SLYR', '&Open MXT…')
        elif self.path().lower().endswith('sxd'):
            action_text = QCoreApplication.translate('SLYR', '&Open ArcScene SXD…')
        elif self.path().lower().endswith('pmf'):
            action_text = QCoreApplication.translate('SLYR', '&Open PMF…')
        elif self.path().lower().endswith('3dd'):
            action_text = QCoreApplication.translate('SLYR', '&Open 3dd…')
        open_action = QAction(action_text, parent)
        open_action.triggered.connect(self.open_mxd)
        return [open_action]


class EsriDatItem(QgsDataItem):
    """
    Data item for .dat files
    """

    def __init__(self, parent, name, path, bookmark=None):
        super().__init__(QgsDataItem.Custom, parent, name, path)
        if not bookmark:
            self.setCapabilities(QgsDataItem.Fertile | QgsDataItem.Collapse)
            self.setToolTip(QDir.toNativeSeparators(path))
        else:
            self.setState(QgsDataItem.Populated)  # no children
            self.setToolTip(bookmark.name())

        self.bookmarks = []
        self.child_items = []
        self.bookmark = bookmark

    def createChildren(self):  # pylint: disable=missing-function-docstring
        # Runs in a thread!
        self.setState(QgsDataItem.Populating)

        error_item = QgsErrorItem(self, "Bookmark conversion requires a licensed version of the SLYR plugin",
                                  self.path() + '/error')
        self.child_items.append(error_item)

    def hasDragEnabled(self):  # pylint: disable=missing-docstring
        return True

    def handleDoubleClick(self):  # pylint: disable=missing-docstring
        self.open_dat()
        return True

    def icon(self):  # pylint: disable=missing-docstring
        if self.bookmark:
            return GuiUtils.get_icon('bookmark.svg')
        else:
            return GuiUtils.get_icon('bookmarks.svg')

    def mimeUri(self):  # pylint: disable=missing-docstring
        if not self.bookmark:
            u = QgsMimeDataUtils.Uri()
            u.layerType = "custom"
            u.providerKey = "esri_dat"
            u.name = self.name()
            u.uri = self.path()
            return u
        else:
            u = QgsMimeDataUtils.Uri()
            u.layerType = "custom"
            u.providerKey = "bookmark"
            u.name = self.name()
            doc = QDomDocument()
            doc.appendChild(self.bookmark.writeXml(doc))
            u.uri = doc.toString()
            return u

    def open_dat(self):
        """
        Handles opening .dat files
        """
        DatDropHandler.open_dat(self.path())

    def zoom_to_bookmark(self):
        """
        Zooms the canvas to a bookmark
        """

        if not self.bookmark:
            return

        try:
            if not iface.mapCanvas().setReferencedExtent(self.bookmark.extent()):
                iface.messageBar().pushWarning("Zoom to Bookmark", "Bookmark extent is empty")
            else:
                iface.mapCanvas().refresh()
        except QgsCsException:
            iface.messageBar().pushWarning("Zoom to Bookmark", "Could not reproject bookmark extent to project CRS.")

    def actions(self, parent):  # pylint: disable=missing-docstring
        if not self.bookmark:
            import_icon = QgsApplication.getThemeIcon("/mActionSharingImport.svg")
            open_action = QAction(import_icon,
                                  QCoreApplication.translate('SLYR', '&Import Spatial Bookmarks to Project'), parent)
            open_action.triggered.connect(self.open_dat)
            return [open_action]
        else:
            zoom_icon = QgsApplication.getThemeIcon("/mActionZoomToLayer.svg")
            zoom_action = QAction(zoom_icon, QCoreApplication.translate('SLYR', 'Zoom to Bookmark'), parent)
            zoom_action.triggered.connect(self.zoom_to_bookmark)
            return [zoom_action]


class SlyrDataItemProvider(QgsDataItemProvider):
    """
    Data item provider for .style/.lyr files
    """

    def name(self):  # pylint: disable=missing-docstring
        return 'slyr'

    def capabilities(self):  # pylint: disable=missing-docstring
        return QgsDataProvider.File

    def createDataItem(self, path, parentItem):  # pylint: disable=missing-docstring
        file_info = QFileInfo(path)

        if file_info.suffix().lower() == 'style':
            return EsriStyleItem(parentItem, file_info.fileName(), path)
        elif file_info.suffix().lower() == 'lyr':
            return EsriLyrItem(parentItem, file_info.fileName(), path)
        elif DatDropHandler.is_bookmark_dat(path):
            return EsriDatItem(parentItem, file_info.fileName(), path)
        elif file_info.suffix().lower() in ('mxd', 'pmf', 'sxd', '3dd', 'mxt'):
            return EsriMxdItem(parentItem, file_info.fileName(), path)
        return None
