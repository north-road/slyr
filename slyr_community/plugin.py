"""
QGIS Plugin interface to SLYR conversions
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
from io import BytesIO
from pathlib import Path
import html

from qgis.PyQt.QtCore import QCoreApplication, QUrl, QDir
from qgis.PyQt.QtWidgets import QAction, QFileDialog, QMenu
from qgis.PyQt import uic, sip
from qgis.PyQt.QtCore import QSettings
from qgis.core import (
    Qgis,
    QgsApplication,
    QgsUnitTypes,
    qgsfunction,
    QgsExpression,
    QgsProject,
    QgsFileUtils,
    QgsLayerTreeLayer,
    QgsMapLayerType,
)
from qgis.gui import QgsOptionsWidgetFactory, QgsOptionsPageWidget, QgsFileWidget

from .bintools.extractor import Extractor
from .converters.context import Context
from .converters.geometry import GeometryConverter

from .parser.exceptions import NotImplementedException
from .parser.initalize_registry import initialize_registry
from .parser.object_registry import REGISTRY
from .parser.stream import Stream
from .qgis_plugin.gui_utils import GuiUtils
from .qgis_plugin.integrations import (
    StyleDropHandler,
    SlyrDataItemProvider,
    LyrDropHandler,
    MxdDropHandler,
    DatDropHandler,
    NameDropHandler,
    LayoutDropHandler,
    MxdProjectOpenHandler,
)
from .qgis_plugin.provider import SlyrProvider
from .qgis_plugin.integrations.browser_utils import BrowserUtils

initialize_registry()

OPTIONS_WIDGET, OPTIONS_BASE = uic.loadUiType(GuiUtils.get_ui_path("settings.ui"))


class ConfigOptionsPage(OPTIONS_WIDGET, QgsOptionsPageWidget):
    """
    SLYR options widget
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.symbol_units.addItem("Points", int(QgsUnitTypes.RenderUnit.RenderPoints))
        self.symbol_units.addItem(
            "Millimeters", int(QgsUnitTypes.RenderUnit.RenderMillimeters)
        )
        self.setObjectName("slyrOptions")
        self.inkscape_path_widget.setStorageMode(QgsFileWidget.StorageMode.GetFile)
        self.mdbtools_path_widget.setStorageMode(QgsFileWidget.StorageMode.GetDirectory)

        if not Extractor.is_windows():
            self.label_mdb_tools_win.hide()

        s = QSettings()
        self.enable_verbose_log.setChecked(
            int(s.value("/plugins/slyr/enable_verbose_log", 0))
        )
        self.convert_font_to_simple_marker.setChecked(
            int(s.value("/plugins/slyr/convert_fonts_to_simple_markers", 1))
        )
        self.convert_font_to_svg.setChecked(
            int(s.value("/plugins/slyr/convert_fonts_to_svg", 1))
        )
        self.replace_http_check.setChecked(
            int(s.value("/plugins/slyr/replace_http", 0))
        )
        self.apply_tweaks.setChecked(int(s.value("/plugins/slyr/apply_tweaks", 1)))
        try:
            symbol_units = s.value("/plugins/slyr/symbol_units")
            if symbol_units is None:
                symbol_units = QgsUnitTypes.RenderUnit.RenderPoints
            else:
                symbol_units = QgsUnitTypes.RenderUnit(int(symbol_units))
            prev_units = symbol_units
        except TypeError:
            prev_units = QgsUnitTypes.RenderUnit.RenderPoints
        except AttributeError:
            prev_units = QgsUnitTypes.RenderUnit.RenderPoints
        self.symbol_units.setCurrentIndex(self.symbol_units.findData(int(prev_units)))
        self.inkscape_path_widget.setFilePath(
            s.value("/plugins/slyr/inkscape_path", "inkscape")
        )
        self.mdbtools_path_widget.setFilePath(
            s.value("/plugins/slyr/mdbtools_path", "")
        )

        self.sde_primary_key_line_edit.setText(
            s.value("/plugins/slyr/sde_primary_key", "OBJECTID")
        )

        self.sde_table_name_conversion_combo.addItem(
            self.tr("Leave Unchanged"), "unchanged"
        )
        self.sde_table_name_conversion_combo.addItem(
            self.tr("Convert to Uppercase"), "upper"
        )
        self.sde_table_name_conversion_combo.addItem(
            self.tr("Convert to Lowercase"), "lower"
        )

        self.sde_table_name_conversion_combo.setCurrentIndex(
            self.sde_table_name_conversion_combo.findData(
                s.value("/plugins/slyr/sde_name_conversion", "unchanged")
            )
        )

    def apply(self):
        """
        Applies the new settings
        """
        s = QSettings()
        s.setValue(
            "/plugins/slyr/enable_annotations",
            0 if not self.enable_annotations.isChecked() else 1,
        )
        s.setValue(
            "/plugins/slyr/convert_layouts",
            0 if not self.enable_layouts.isChecked() else 1,
        )
        s.setValue(
            "/plugins/slyr/convert_fonts_to_simple_markers",
            0 if not self.convert_font_to_simple_marker.isChecked() else 1,
        )
        s.setValue(
            "/plugins/slyr/convert_font_to_svg",
            0 if not self.convert_font_to_svg.isChecked() else 1,
        )
        s.setValue("/plugins/slyr/symbol_units", self.symbol_units.currentData())
        s.setValue("/plugins/slyr/picture_store_folder", self.picture_store.filePath())
        s.setValue("/plugins/slyr/inkscape_path", self.inkscape_path_widget.filePath())
        s.setValue("/plugins/slyr/mdbtools_path", self.mdbtools_path_widget.filePath())
        s.setValue(
            "/plugins/slyr/store_relative",
            0 if not self.store_relative.isChecked() else 1,
        )
        s.setValue(
            "/plugins/slyr/embed_pictures",
            0 if not self.embed_pictures.isChecked() else 1,
        )
        s.setValue(
            "/plugins/slyr/apply_tweaks", 0 if not self.apply_tweaks.isChecked() else 1
        )


class SlyrOptionsFactory(QgsOptionsWidgetFactory):
    """
    Factory class for SLYR options widget
    """

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    def icon(self):  # pylint: disable=missing-function-docstring
        return GuiUtils.get_icon("icon.svg")

    def createWidget(self, parent):  # pylint: disable=missing-function-docstring
        return ConfigOptionsPage(parent)


class SlyrPlugin:
    """
    SLYR *air guitar* SCREEEEEAAAAAMMM
    """

    def __init__(self, iface):
        """init"""
        self.iface = iface
        self.provider = SlyrProvider()
        self.drop_handler = StyleDropHandler()
        self.lyr_drop_handler = LyrDropHandler()
        self.mxd_drop_handler = MxdDropHandler()
        self.dat_drop_handler = DatDropHandler()
        self.name_drop_handler = NameDropHandler()
        self.item_provider = SlyrDataItemProvider()
        self.layout_drop_handler = LayoutDropHandler()
        self.options_factory = None
        self.open_handler = None

    def initGui(self):
        """startup"""
        self.initProcessing()
        self.iface.registerCustomDropHandler(self.drop_handler)
        self.iface.registerCustomDropHandler(self.lyr_drop_handler)
        self.iface.registerCustomDropHandler(self.mxd_drop_handler)
        self.iface.registerCustomDropHandler(self.dat_drop_handler)
        self.iface.registerCustomDropHandler(self.name_drop_handler)
        self.iface.registerCustomLayoutDropHandler(self.layout_drop_handler)
        QgsApplication.dataItemProviderRegistry().addProvider(self.item_provider)

        self.options_factory = SlyrOptionsFactory()
        self.options_factory.setTitle("SLYR")
        self.iface.registerOptionsWidgetFactory(self.options_factory)

        if MxdProjectOpenHandler is not None:
            self.open_handler = MxdProjectOpenHandler()
            self.iface.registerCustomProjectOpenHandler(self.open_handler)

    def initProcessing(self):
        """Create the Processing provider"""
        QgsApplication.processingRegistry().addProvider(self.provider)

    def unload(self):
        """teardown"""
        QgsApplication.processingRegistry().removeProvider(self.provider)
        QgsApplication.dataItemProviderRegistry().removeProvider(self.item_provider)
        self.iface.unregisterCustomDropHandler(self.drop_handler)
        self.iface.unregisterCustomDropHandler(self.lyr_drop_handler)
        self.iface.unregisterCustomDropHandler(self.mxd_drop_handler)
        self.iface.unregisterCustomDropHandler(self.dat_drop_handler)
        self.iface.unregisterCustomDropHandler(self.name_drop_handler)
        self.iface.unregisterOptionsWidgetFactory(self.options_factory)
        self.iface.unregisterCustomLayoutDropHandler(self.layout_drop_handler)

        if MxdProjectOpenHandler is not None:
            self.iface.unregisterCustomProjectOpenHandler(self.open_handler)
