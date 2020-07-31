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

from qgis.core import (
    Qgis,
    QgsApplication,
    QgsUnitTypes,
    QgsExpression
)

from qgis.gui import (
    QgsOptionsWidgetFactory,
    QgsOptionsPageWidget,
    QgsFileWidget
)
from qgis.PyQt.QtCore import QSettings
from slyr_community.qgis_plugin.provider import SlyrProvider
from slyr_community.parser.initalize_registry import initialize_registry
from slyr_community.parser.object_registry import REGISTRY
from slyr_community.qgis_plugin.integrations.browser import (
    StyleDropHandler,
    SlyrDataItemProvider,
    LyrDropHandler,
    MxdDropHandler,
    DatDropHandler,
    NameDropHandler,
    LayoutDropHandler,
    USE_PROJECT_OPEN_HANDLER,
)
try:
    from slyr.qgis_plugin.integrations.browser import MxdProjectOpenHandler
except ImportError:
    pass

from slyr_community.qgis_plugin.gui_utils import GuiUtils

from qgis.PyQt import uic

initialize_registry()

OPTIONS_WIDGET, OPTIONS_BASE = uic.loadUiType(
    GuiUtils.get_ui_path('settings.ui'))


class ConfigOptionsPage(OPTIONS_WIDGET, QgsOptionsPageWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.symbol_units.addItem('Points', QgsUnitTypes.RenderPoints)
        self.symbol_units.addItem('Millimeters', QgsUnitTypes.RenderMillimeters)
        self.setObjectName('slyrOptions')
        self.picture_store.setStorageMode(QgsFileWidget.GetDirectory)
        self.inkscape_path_widget.setStorageMode(QgsFileWidget.GetFile)

        s = QSettings()
        self.key_line_edit.setText(s.value('/plugins/slyr/license'))
        self.enable_annotations.setChecked(int(s.value('/plugins/slyr/enable_annotations', 0)))
        self.enable_layouts.setChecked(int(s.value('/plugins/slyr/convert_layouts', 1)))
        self.convert_font_to_svg.setChecked(int(s.value('/plugins/slyr/convert_font_to_svg', 0)))
        self.store_relative.setChecked(int(s.value('/plugins/slyr/store_relative', 0)))
        self.embed_pictures.setChecked(int(s.value('/plugins/slyr/embed_pictures', Qgis.QGIS_VERSION_INT >= 30600)))
        self.apply_tweaks.setChecked(int(s.value('/plugins/slyr/apply_tweaks', 1)))
        prev_units = int(s.value('/plugins/slyr/symbol_units', int(QgsUnitTypes.RenderPoints)))
        self.symbol_units.setCurrentIndex(self.symbol_units.findData(prev_units))
        self.picture_store.setFilePath(s.value('/plugins/slyr/picture_store_folder', ''))
        self.inkscape_path_widget.setFilePath(s.value('/plugins/slyr/inkscape_path', 'inkscape'))

    def apply(self):
        s = QSettings()
        s.setValue('/plugins/slyr/enable_annotations', 0 if not self.enable_annotations.isChecked() else 1)
        s.setValue('/plugins/slyr/convert_layouts', 0 if not self.enable_layouts.isChecked() else 1)
        s.setValue('/plugins/slyr/convert_font_to_svg', 0 if not self.convert_font_to_svg.isChecked() else 1)
        s.setValue('/plugins/slyr/symbol_units', self.symbol_units.currentData())
        s.setValue('/plugins/slyr/picture_store_folder', self.picture_store.filePath())
        s.setValue('/plugins/slyr/inkscape_path', self.inkscape_path_widget.filePath())
        s.setValue('/plugins/slyr/store_relative', 0 if not self.store_relative.isChecked() else 1)
        s.setValue('/plugins/slyr/embed_pictures', 0 if not self.embed_pictures.isChecked() else 1)
        s.setValue('/plugins/slyr/apply_tweaks', 0 if not self.apply_tweaks.isChecked() else 1)


class SlyrOptionsFactory(QgsOptionsWidgetFactory):

    def __init__(self):
        super().__init__()

    def icon(self):
        return GuiUtils.get_icon('icon.svg')

    def createWidget(self, parent):
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
        self.options_factory.setTitle('SLYR')
        self.iface.registerOptionsWidgetFactory(self.options_factory)

        if USE_PROJECT_OPEN_HANDLER:
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

        if USE_PROJECT_OPEN_HANDLER:
            self.iface.unregisterCustomProjectOpenHandler(self.open_handler)

