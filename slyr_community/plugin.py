# -*- coding: utf-8 -*-

# /***************************************************************************
# plugin.py
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
QGIS Plugin interface to SLYR conversions
"""

from qgis.core import Qgis, QgsApplication, QgsUnitTypes
from qgis.gui import QgsOptionsWidgetFactory, QgsOptionsPageWidget, QgsFileWidget

from qgis.PyQt.QtCore import QSettings
from qgis.PyQt import uic

from .bintools.extractor import Extractor
from .qgis_plugin.provider import SlyrProvider
from .parser.initalize_registry import initialize_registry
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
from .qgis_plugin.gui_utils import GuiUtils

initialize_registry()

OPTIONS_WIDGET, OPTIONS_BASE = uic.loadUiType(GuiUtils.get_ui_path("settings.ui"))


class ConfigOptionsPage(OPTIONS_WIDGET, QgsOptionsPageWidget):
    """
    SLYR options widget
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.symbol_units.addItem("Points", int(QgsUnitTypes.RenderPoints))
        self.symbol_units.addItem("Millimeters", int(QgsUnitTypes.RenderMillimeters))
        self.setObjectName("slyrOptions")
        self.picture_store.setStorageMode(QgsFileWidget.GetDirectory)
        self.inkscape_path_widget.setStorageMode(QgsFileWidget.GetFile)
        self.mdbtools_path_widget.setStorageMode(QgsFileWidget.GetDirectory)

        if not Extractor.is_windows():
            self.label_mdb_tools_win.hide()

        s = QSettings()
        self.enable_annotations.setChecked(
            int(s.value("/plugins/slyr/enable_annotations", 0))
        )
        self.enable_layouts.setChecked(int(s.value("/plugins/slyr/convert_layouts", 1)))
        self.convert_font_to_simple_marker.setChecked(
            int(s.value("/plugins/slyr/convert_fonts_to_simple_markers", 1))
        )
        self.convert_font_to_svg.setChecked(
            int(s.value("/plugins/slyr/convert_font_to_svg", 0))
        )
        self.store_relative.setChecked(int(s.value("/plugins/slyr/store_relative", 0)))
        self.embed_pictures.setChecked(
            int(s.value("/plugins/slyr/embed_pictures", Qgis.QGIS_VERSION_INT >= 30600))
        )
        self.apply_tweaks.setChecked(int(s.value("/plugins/slyr/apply_tweaks", 1)))

        try:
            symbol_units = s.value("/plugins/slyr/symbol_units")
            if symbol_units is None:
                symbol_units = QgsUnitTypes.RenderPoints
            else:
                symbol_units = QgsUnitTypes.RenderUnit(int(symbol_units))
            prev_units = symbol_units
        except TypeError:
            prev_units = QgsUnitTypes.RenderPoints
        except AttributeError:
            prev_units = QgsUnitTypes.RenderPoints
        self.symbol_units.setCurrentIndex(self.symbol_units.findData(int(prev_units)))

        self.picture_store.setFilePath(
            s.value("/plugins/slyr/picture_store_folder", "")
        )
        self.inkscape_path_widget.setFilePath(
            s.value("/plugins/slyr/inkscape_path", "inkscape")
        )
        self.mdbtools_path_widget.setFilePath(
            s.value("/plugins/slyr/mdbtools_path", "")
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
