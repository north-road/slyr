# -*- coding: utf-8 -*-
"""Data source select dialog. Ported from QGIS 3.6 master.

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

__author__ = "(C) 2018 by Nyall Dawson"
__date__ = "24/10/2018"
__copyright__ = "Copyright 2018, North Road"
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = "$Format:%H$"

import os
from qgis.PyQt.uic import loadUiType
from qgis.core import QgsBrowserProxyModel, QgsMimeDataUtils, QgsLayerItem
from qgis.gui import QgsGui
from qgis.utils import iface
from qgis.PyQt.QtWidgets import QDialogButtonBox, QLabel

path = os.path.dirname(os.path.abspath(__file__))
ui, base = loadUiType(os.path.join(path, "ui", "datasourceselectdialog.ui"))


class DataSourceSelectDialog(base, ui):
    """
    Reusable dialog for selecting a map layer source based on the QGIS browser.
    Allows for selection of disk based layers, together with layers from database
    and online providers (such as Oracle/Postgres/etc)
    """

    def __init__(self, layer_name, original_uri, layer_type, parent=None):
        super().__init__(parent)

        self.setupUi(self)
        self.setWindowTitle("Select Source for {}".format(layer_name))
        QgsGui.enableAutoGeometryRestore(self)

        # in case browser panel isn't open, we need to force initialize the model now
        iface.browserModel().initialize()

        self.browser_proxy_model = QgsBrowserProxyModel(self)
        self.browser_proxy_model.setBrowserModel(iface.browserModel())
        self.browser_proxy_model.setFilterByLayerType(True)
        self.browser_proxy_model.setLayerType(layer_type)
        self.mBrowserTreeView.setHeaderHidden(True)
        self.mBrowserTreeView.setModel(self.browser_proxy_model)
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        self.mBrowserTreeView.clicked.connect(self.on_layer_selected)
        self.uri = None
        self.description_label = None
        self.setDescription("Original source: {}".format(original_uri))

    def setDescription(self, description):
        """
        Sets the description to show in the dialog
        """
        if description:
            if not self.description_label:
                self.description_label = QLabel()
                self.description_label.setWordWrap(True)
                self.description_label.setMargin(4)
                self.verticalLayout.insertWidget(1, self.description_label)
            self.description_label.setText(description)
        else:
            if self.description_label:
                self.verticalLayout.removeWidget(self.description_label)
                self.description_label.deleteLater()
                self.description_label = None

    def on_layer_selected(self, index):
        """
        Triggered on selecting a layer
        """
        is_layer_compatible = False
        self.uri = QgsMimeDataUtils.Uri()
        if index.isValid():
            item = self.browser_proxy_model.dataItem(index)
            if item:
                if issubclass(item.__class__, QgsLayerItem):
                    is_layer_compatible = True
                    self.uri = item.mimeUri()

        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(is_layer_compatible)
