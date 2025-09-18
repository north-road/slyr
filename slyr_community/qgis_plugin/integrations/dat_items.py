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
Browser and app integrations for dat file integration with QGIS
"""

from qgis.PyQt.QtCore import QDir, QCoreApplication
from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtXml import QDomDocument
from qgis.core import (
    QgsApplication,
    Qgis,
    QgsDataItem,
    QgsErrorItem,
    QgsMimeDataUtils,
    QgsCsException,
)
from qgis.gui import QgsCustomDropHandler
from qgis.utils import iface

from ...qgis_plugin.gui_utils import GuiUtils
from ...qgis_plugin.integrations.browser_utils import BrowserUtils


class DatDropHandler(QgsCustomDropHandler):
    """
    .dat bookmarks file drop handler
    """

    @staticmethod
    def is_bookmark_dat(file):
        """
        Tests whether a file is an ESRI bookmark dat file
        """
        if not file.lower().endswith(".dat"):
            return False
        # check for file signature
        with open(file, "rb") as f:
            try:
                if not f.read(4) == b"\xd0\xcf\x11\xe0":
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
        BrowserUtils.show_warning(
            "Licensed version required",
            "Convert Bookmarks",
            message,
            level=Qgis.Critical,
            message_bar=iface.messageBar(),
        )

        return True

    def customUriProviderKey(self):  # pylint: disable=missing-docstring
        return "esri_dat"

    def handleCustomUriDrop(self, uri):  # pylint: disable=missing-docstring
        path = uri.uri
        self.open_dat(path)


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

        error_item = QgsErrorItem(
            self,
            "Bookmark conversion requires a licensed version of the SLYR plugin",
            self.path() + "/error",
        )
        self.child_items.append(error_item)
        return self.child_items

    def hasDragEnabled(self):  # pylint: disable=missing-docstring
        return True

    def handleDoubleClick(self):  # pylint: disable=missing-docstring
        self.open_dat()
        return True

    def icon(self):  # pylint: disable=missing-docstring
        if self.bookmark:
            return GuiUtils.get_icon("bookmark.svg")
        else:
            return GuiUtils.get_icon("bookmarks.svg")

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

    def mimeUris(self):  # pylint: disable=missing-docstring
        return [self.mimeUri()]

    def open_dat(self):
        """
        Handles opening .dat files
        """
        return DatDropHandler.open_dat(self.path())

    def zoom_to_bookmark(self):
        """
        Zooms the canvas to a bookmark
        """

        if not self.bookmark:
            return

        try:
            if not iface.mapCanvas().setReferencedExtent(self.bookmark.extent()):
                iface.messageBar().pushWarning(
                    "Zoom to Bookmark", "Bookmark extent is empty"
                )
            else:
                iface.mapCanvas().refresh()
        except QgsCsException:
            iface.messageBar().pushWarning(
                "Zoom to Bookmark",
                "Could not reproject bookmark extent to project CRS.",
            )

    def actions(self, parent):  # pylint: disable=missing-docstring
        if not self.bookmark:
            import_icon = QgsApplication.getThemeIcon("/mActionSharingImport.svg")
            open_action = QAction(
                import_icon,
                QCoreApplication.translate(
                    "SLYR", "&Import Spatial Bookmarks to Project"
                ),
                parent,
            )
            open_action.triggered.connect(self.open_dat)
            return [open_action]
        else:
            zoom_icon = QgsApplication.getThemeIcon("/mActionZoomToLayer.svg")
            zoom_action = QAction(
                zoom_icon,
                QCoreApplication.translate("SLYR", "Zoom to Bookmark"),
                parent,
            )
            zoom_action.triggered.connect(self.zoom_to_bookmark)
            return [zoom_action]
