"""
Browser and app integrations for dat file integration with QGIS
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

from qgis.PyQt.QtCore import QDir, QCoreApplication
from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtXml import QDomDocument
from qgis.core import (
    QgsApplication,
    Qgis,
    QgsDataItem,
    QgsMimeDataUtils,
    QgsProject,
    QgsCsException,
)
from qgis.gui import QgsCustomDropHandler
from qgis.utils import iface

from ...converters.bookmarks import BookmarkConverter
from ...converters.context import Context
from ...parser.stream import Stream
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
    def get_bookmarks(input_file):  # pylint: disable=too-many-locals
        """
        Returns a list of bookmarks from a file
        """
        bookmarks = []
        warnings = set()
        errors = set()
        info = set()
        with open(input_file, "rb") as f:
            stream = Stream(
                f, False, force_layer=True, offset=-1, path="PlaceCollection"
            )
            stream.is_layer = False

            version = stream.read_ushort("version")
            if version > 1:
                return None

            context = Context()
            context.project = QgsProject.instance()

            bookmark_name = ""

            def unsupported_object_callback(msg, level=Context.WARNING):
                if level == Context.WARNING:
                    warnings.add("<b>{}</b>: {}".format(bookmark_name, msg))
                elif level == Context.CRITICAL:
                    errors.add("<b>{}</b>: {}".format(bookmark_name, msg))
                elif level == Context.INFO:
                    info.add("<b>{}</b>: {}".format(bookmark_name, msg))

            context.unsupported_object_callback = unsupported_object_callback

            count = stream.read_int("count")
            for _ in range(count):
                b = stream.read_object("bookmark", allow_reference=False)
                bookmark_name = b.name
                bookmark = BookmarkConverter.convert_bookmark(b.name, b.extent, context)
                if bookmark is not None:
                    bookmarks.append(bookmark)

        if warnings or errors or info:
            message = ""
            title = ""
            level = None

            if errors:
                message = "<p>The following errors were generated while converting the bookmark file:</p>"
                message += "<ul>"
                for w in errors:
                    message += "<li>{}</li>".format(
                        html.escape(w).replace("\n", "<br>")
                    )
                message += "</ul>"
                title = "DAT could not be completely converted"
                level = Qgis.MessageLevel.Critical

            if warnings:
                if message:
                    message += "<p>Additionally, some warnings were generated:</p>"
                else:
                    message += "<p>The following warnings were generated while converting the bookmark file:</p>"
                message += "<ul>"
                for w in warnings:
                    message += "<li>{}</li>".format(
                        html.escape(w).replace("\n", "<br>")
                    )
                message += "</ul>"
                if not title:
                    title = "DAT could not be completely converted"
                if level is None:
                    level = Qgis.MessageLevel.Warning

            if info:
                if message:
                    message += (
                        "<p>Additionally, some extra messages were generated:</p>"
                    )
                else:
                    message += "<p>The following information messages were generated converting the DAT file:</p>"
                message += "<ul>"
                for w in info:
                    message += "<li>{}</li>".format(
                        html.escape(w).replace("\n", "<br>")
                    )
                message += "</ul>"
                if not title:
                    title = "Some messages were generated while converting the DAT file"
                if level is None:
                    level = Qgis.MessageLevel.Info

            BrowserUtils.show_warning(title, "Convert DAT", message, level=level)

        return bookmarks

    @staticmethod
    def open_dat(input_file):
        """
        Opens a dat bookmark file in the current project
        """

        bookmarks = DatDropHandler.get_bookmarks(input_file)
        if bookmarks:
            for b in bookmarks:
                QgsProject.instance().bookmarkManager().addBookmark(b)

            iface.messageBar().pushSuccess(
                "SLYR",
                "{} bookmarks were successfully added to the current project".format(
                    len(bookmarks)
                ),
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
        super().__init__(QgsDataItem.Type.Custom, parent, name, path)
        if not bookmark:
            self.setCapabilities(
                QgsDataItem.Capability.Fertile | QgsDataItem.Capability.Collapse
            )
            self.setToolTip(QDir.toNativeSeparators(path))
        else:
            self.setState(QgsDataItem.State.Populated)  # no children
            self.setToolTip(bookmark.name())

        self.bookmarks = []
        self.child_items = []
        self.bookmark = bookmark

    def createChildren(self):  # pylint: disable=missing-function-docstring
        # Runs in a thread!

        self.setState(QgsDataItem.State.Populating)

        self.bookmarks = DatDropHandler.get_bookmarks(self.path())
        if self.bookmarks:
            for b in self.bookmarks:
                self.child_items.append(
                    EsriDatItem(self, b.name(), self.path() + "/" + b.name(), b)
                )

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
