"""
Browser and app integrations for STYLE file integration with QGIS
"""

# /***************************************************************************
#  *                                                                         *
#  *   This program is free software; you can redistribute it and/or modify  *
#  *   it under the terms of the GNU General Public License as published by  *
#  *   the Free Software Foundation; either version 2 of the License, or     *
#  *   (at your option) any later version.                                   *
#  *                                                                         *
#  ***************************************************************************/

import html
from functools import partial
from io import BytesIO

from processing import execAlgorithmDialog
from qgis.PyQt.QtCore import QFileInfo, QDir, QCoreApplication
from qgis.PyQt.QtWidgets import QAction, QProgressDialog, QPushButton
from qgis.core import (
    Qgis,
    QgsDataItem,
    QgsMimeDataUtils,
    QgsStyle,
    QgsFeedback,
    QgsSymbol,
    QgsColorRamp,
    QgsTextFormat,
    QgsPalLayerSettings,
    QgsProject,
)
from qgis.gui import QgsCustomDropHandler, QgsStyleManagerDialog
from qgis.utils import iface

from .browser_utils import BrowserUtils
from ..gui_utils import GuiUtils

from ...bintools.extractor import Extractor, MissingBinaryException
from ...converters.context import Context
from ...converters.geometry import GeometryConverter
from ...converters.symbols import SymbolConverter

from ...parser.exceptions import (
    UnreadableSymbolException,
    UnsupportedVersionException,
    NotImplementedException,
    UnknownClsidException,
    UnreadablePictureException,
)

from ...parser.stream import Stream

try:
    from qgis.core import QgsLegendPatchShape  # pylint: disable=ungrouped-imports
except ImportError:
    QgsLegendPatchShape = None


class StyleDropHandler(QgsCustomDropHandler):
    """
    .style file drop handler
    """

    def handleFileDrop(self, file):  # pylint: disable=missing-docstring
        if file.lower().endswith(".style"):
            return self.open_style(file)
        if file.lower().endswith(".stylx"):
            return self.open_stylx(file)

        return False

    @staticmethod
    def open_style(input_file):  # pylint: disable=too-many-locals,too-many-branches,too-many-statements
        """
        Opens a .style file
        """

        if (
            input_file.lower().endswith(".style")
            and not Extractor.is_mdb_tools_binary_available()
        ):
            message_bar = iface.messageBar()
            widget = message_bar.createMessage("SLYR", "MDB Tools utility not found")
            settings_button = QPushButton(
                "Configure…", pressed=partial(BrowserUtils.open_settings, widget)
            )
            widget.layout().addWidget(settings_button)
            message_bar.pushWidget(widget, Qgis.MessageLevel.Critical)
            return True

        style = QgsStyle()
        style.createMemoryDatabase()

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

        feedback = QgsFeedback()

        progress_dialog = QProgressDialog(
            "Loading style database…", "Abort", 0, 100, None
        )
        progress_dialog.setWindowTitle("Loading Style")

        def progress_changed(progress: float):
            """
            Handles feedback to progress dialog bridge
            """
            progress_dialog.setValue(int(progress))
            iterations = 0
            while iterations < 100:
                QCoreApplication.processEvents()
                iterations += 1

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
        info = set()

        types_to_extract = [
            Extractor.FILL_SYMBOLS,
            Extractor.LINE_SYMBOLS,
            Extractor.MARKER_SYMBOLS,
            Extractor.COLOR_RAMPS,
            Extractor.TEXT_SYMBOLS,
            Extractor.LABELS,
            Extractor.MAPLEX_LABELS,
            Extractor.AREA_PATCHES,
            Extractor.LINE_PATCHES,
            Extractor.REPRESENTATION_RULES,
        ]

        type_percent = 100 / len(types_to_extract)

        for type_index, symbol_type in enumerate(types_to_extract):
            try:
                raw_symbols = Extractor.extract_styles(input_file, symbol_type)
            except MissingBinaryException:
                BrowserUtils.show_warning(
                    "MDB Tools utility not found",
                    "Convert style",
                    'The MDB tools "mdb-export" utility is required to convert .style databases. Please setup a path to the MDB tools utility in the SLYR options panel.',
                    level=Qgis.MessageLevel.Critical,
                )
                progress_dialog.deleteLater()
                return True

            if feedback.isCanceled():
                break

            for index, raw_symbol in enumerate(raw_symbols):
                feedback.setProgress(
                    int(
                        index / len(raw_symbols) * type_percent
                        + type_percent * type_index
                    )
                )
                if feedback.isCanceled():
                    break
                name = raw_symbol[Extractor.NAME]
                if not name:
                    name = "unnamed"

                tags = raw_symbol[Extractor.TAGS].split(";")

                unique_name = make_name_unique(name)

                handle = BytesIO(raw_symbol[Extractor.BLOB])
                stream = Stream(handle)
                stream.allow_shortcuts = False

                try:
                    symbol = stream.read_object()
                except UnreadableSymbolException as e:
                    e = "Unreadable object: {}".format(e)
                    unreadable.append(
                        "<b>{}</b>: {}".format(html.escape(name), html.escape(str(e)))
                    )
                    continue
                except NotImplementedException as e:
                    unreadable.append(
                        "<b>{}</b>: {}".format(html.escape(name), html.escape(str(e)))
                    )
                    continue
                except UnsupportedVersionException as e:
                    e = "Unsupported version: {}".format(e)
                    unreadable.append(
                        "<b>{}</b>: {}".format(html.escape(name), html.escape(str(e)))
                    )
                    continue
                except UnknownClsidException as e:
                    unreadable.append(
                        "<b>{}</b>: {}".format(html.escape(name), html.escape(str(e)))
                    )
                    continue
                except UnreadablePictureException as e:
                    unreadable.append(
                        "<b>{}</b>: {}".format(html.escape(name), html.escape(str(e)))
                    )
                    continue

                context = Context()
                context.project = QgsProject.instance()
                context.symbol_name = unique_name

                def unsupported_object_callback(msg, level=Context.WARNING):
                    if level == Context.WARNING:
                        warnings.add(
                            "<b>{}</b>: {}".format(
                                html.escape(unique_name),  # pylint: disable=cell-var-from-loop
                                html.escape(msg),
                            )
                        )
                    elif level == Context.CRITICAL:
                        errors.add(
                            "<b>{}</b>: {}".format(
                                html.escape(unique_name),  # pylint: disable=cell-var-from-loop
                                html.escape(msg),
                            )
                        )
                    elif level == Context.INFO:
                        info.add(
                            "<b>{}</b>: {}".format(
                                html.escape(unique_name),  # pylint: disable=cell-var-from-loop
                                html.escape(msg),
                            )
                        )

                context.unsupported_object_callback = unsupported_object_callback

                if symbol_type in (Extractor.AREA_PATCHES, Extractor.LINE_PATCHES):
                    if symbol_type == Extractor.LINE_PATCHES:
                        geom = GeometryConverter.convert_geometry(symbol.polyline)
                        qgis_symbol = QgsLegendPatchShape(
                            QgsSymbol.SymbolType.Line, geom, symbol.preserve_aspect
                        )
                    elif symbol_type == Extractor.AREA_PATCHES:
                        geom = GeometryConverter.convert_geometry(symbol.polygon)
                        qgis_symbol = QgsLegendPatchShape(
                            QgsSymbol.SymbolType.Fill, geom, symbol.preserve_aspect
                        )
                else:
                    try:
                        qgis_symbol = SymbolConverter.Symbol_to_QgsSymbol(
                            symbol, context
                        )
                    except NotImplementedException as e:
                        unreadable.append(
                            "<b>{}</b>: {}".format(
                                html.escape(name), html.escape(str(e))
                            )
                        )
                        continue
                    except UnreadablePictureException as e:
                        unreadable.append(
                            "<b>{}</b>: {}".format(
                                html.escape(name), html.escape(str(e))
                            )
                        )
                        continue

                if isinstance(qgis_symbol, QgsSymbol):
                    # self.check_for_missing_fonts(qgis_symbol, feedback)
                    style.addSymbol(unique_name, qgis_symbol, True)
                elif isinstance(qgis_symbol, QgsColorRamp):
                    style.addColorRamp(unique_name, qgis_symbol, True)
                elif isinstance(qgis_symbol, QgsTextFormat):
                    style.addTextFormat(unique_name, qgis_symbol, True)
                elif isinstance(qgis_symbol, QgsPalLayerSettings):
                    style.addLabelSettings(unique_name, qgis_symbol, True)
                elif isinstance(qgis_symbol, QgsLegendPatchShape):
                    style.addLegendPatchShape(unique_name, qgis_symbol, True)

                if tags:
                    if isinstance(qgis_symbol, QgsSymbol):
                        assert style.tagSymbol(
                            QgsStyle.StyleEntity.SymbolEntity, unique_name, tags
                        )
                    elif isinstance(qgis_symbol, QgsColorRamp):
                        assert style.tagSymbol(
                            QgsStyle.StyleEntity.ColorrampEntity, unique_name, tags
                        )
                    elif isinstance(qgis_symbol, QgsTextFormat) and hasattr(
                        QgsStyle, "TextFormatEntity"
                    ):
                        assert style.tagSymbol(
                            QgsStyle.StyleEntity.TextFormatEntity, unique_name, tags
                        )
                    elif isinstance(qgis_symbol, QgsPalLayerSettings) and hasattr(
                        QgsStyle, "LabelSettingsEntity"
                    ):
                        assert style.tagSymbol(
                            QgsStyle.StyleEntity.LabelSettingsEntity, unique_name, tags
                        )
                    elif isinstance(qgis_symbol, QgsLegendPatchShape):
                        assert style.tagSymbol(
                            QgsStyle.StyleEntity.LegendPatchShapeEntity,
                            unique_name,
                            tags,
                        )
        progress_dialog.deleteLater()
        if feedback.isCanceled():
            return True

        if errors or unreadable or warnings or info:
            message = ""
            title = ""
            level = None

            if unreadable:
                message = "<p>The following symbols could not be converted:</p>"
                message += "<ul>"
                for w in unreadable:
                    message += "<li>{}</li>".format(w.replace("\n", "<br>"))
                message += "</ul>"
                title = "style could not be completely converted"
                level = Qgis.MessageLevel.Critical

            if errors:
                message += "<p>The following errors were generated while converting symbols:</p>"
                message += "<ul>"
                for w in errors:
                    message += "<li>{}</li>".format(w.replace("\n", "<br>"))
                message += "</ul>"
                if not title:
                    title = "style could not be completely converted"
                if level is None:
                    level = Qgis.MessageLevel.Critical

            if warnings:
                message += "<p>The following warnings were generated while converting symbols:</p>"
                message += "<ul>"
                for w in warnings:
                    message += "<li>{}</li>".format(w.replace("\n", "<br>"))
                message += "</ul>"
                if not title:
                    title = "style could not be completely converted"
                if level is None:
                    level = Qgis.MessageLevel.Warning

            if info:
                if message:
                    message += (
                        "<p>Additionally, some extra messages were generated:</p>"
                    )
                else:
                    message += "<p>The following information messages were generated converting symbols:</p>"
                message += "<ul>"
                for w in info:
                    message += "<li>{}</li>".format(
                        html.escape(w).replace("\n", "<br>")
                    )
                message += "</ul>"
                if not title:
                    title = "Some messages were generated while converting style"
                if level is None:
                    level = Qgis.MessageLevel.Info

            BrowserUtils.show_warning(title, "Convert style", message, level=level)

        dlg = QgsStyleManagerDialog(style, readOnly=True)
        dlg.setFavoritesGroupVisible(False)
        dlg.setSmartGroupsVisible(False)
        fi = QFileInfo(input_file)
        dlg.setBaseStyleName(fi.baseName())

        dlg.setWindowTitle(fi.baseName())
        dlg.exec()
        return True

    @staticmethod
    def open_stylx(input_file):  # pylint: disable=too-many-locals,too-many-branches,too-many-statements
        """
        Opens a .stylx file
        """
        message = '<p>This functionality requires the licensed version of SLYR. Please see <a href="https://north-road.com/slyr/">here</a> for details.</p>'
        BrowserUtils.show_warning(
            "Licensed version required", "Convert MXD", message, level=Qgis.Critical
        )
        return True

    def customUriProviderKey(self):  # pylint: disable=missing-docstring
        return "esri_style"

    def handleCustomUriDrop(self, uri):  # pylint: disable=missing-docstring
        path = uri.uri
        self.open_style(path)


class EsriStyleItem(QgsDataItem):
    """
    Data item for .style files
    """

    def __init__(self, parent, name, path):
        super().__init__(QgsDataItem.Type.Custom, parent, name, path)
        self.setState(QgsDataItem.State.Populated)  # no children
        self.setToolTip(QDir.toNativeSeparators(path))

    def hasDragEnabled(self):  # pylint: disable=missing-docstring
        return True

    def handleDoubleClick(self):  # pylint: disable=missing-docstring
        self.open_style()
        return True

    def icon(self):  # pylint: disable=missing-docstring
        return GuiUtils.get_icon("icon.svg")

    def mimeUri(self):  # pylint: disable=missing-docstring
        u = QgsMimeDataUtils.Uri()
        u.layerType = "custom"
        u.providerKey = "esri_style"
        u.name = self.name()
        u.uri = self.path()
        return u

    def mimeUris(self):  # pylint: disable=missing-docstring
        return [self.mimeUri()]

    def open_style(self):
        """
        Opens a STYLE file in the current project
        """
        StyleDropHandler.open_style(self.path())

    def convert_style(self):
        """
        Executes the style to xml conversion algorithm
        """

        execAlgorithmDialog("slyr:styletoqgisxml", {"INPUT": self.path()})

    def actions(self, parent):  # pylint: disable=missing-docstring
        open_action = QAction(
            QCoreApplication.translate("SLYR", "&Open Style…"), parent
        )
        open_action.triggered.connect(self.open_style)
        convert_action = QAction(
            QCoreApplication.translate("SLYR", "&Convert Style…"), parent
        )
        convert_action.triggered.connect(self.convert_style)
        return [open_action, convert_action]
