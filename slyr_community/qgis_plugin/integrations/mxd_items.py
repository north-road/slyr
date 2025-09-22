"""
Browser and app integrations for MXD/PMF/SXD/MXT file integration with QGIS
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
from pathlib import PureWindowsPath

from qgis.PyQt.QtCore import QDir, QCoreApplication, QTimer
from qgis.PyQt.QtWidgets import QAction
from qgis.core import (
    Qgis,
    QgsDataItem,
    QgsMimeDataUtils,
    QgsProject,
    QgsProjectDirtyBlocker,
)
from qgis.gui import QgsCustomDropHandler
from qgis.utils import iface

from .browser_utils import BrowserUtils
from .mxd_browser_widget import MxdBrowserWidget
from ..gui_utils import GuiUtils
from ...converters.context import Context
from ...converters.project import ProjectConverter
from ...parser.exceptions import EmptyDocumentException, DocumentTypeException
from ...parser.exceptions import RequiresLicenseException
from ...parser.objects.map import Map
from ...parser.stream import Stream
from ...parser.streams.map_document import MapDocument

try:
    from qgis.gui import QgsCustomProjectOpenHandler  # pylint: disable=ungrouped-imports
except ImportError:
    QgsCustomProjectOpenHandler = None

blocker = None


class MxdDropHandler(QgsCustomDropHandler):
    """
    .mxd/.pmf/.sxd/.3dd file drop handler
    """

    def handleFileDrop(self, file):  # pylint: disable=missing-docstring
        if not (
            file.lower().endswith(".mxd")
            or file.lower().endswith(".sxd")
            or file.lower().endswith(".pmf")
            or file.lower().endswith(".3dd")
            or file.lower().endswith(".mxt")
        ):
            return False
        return self.open_mxd(file)

    @staticmethod
    def open_mxd(input_file, use_warnings=True):  # pylint:disable=too-many-locals,too-many-return-statements,too-many-branches,too-many-statements
        """
        Opens an MXD file in the current project
        """
        global blocker  # pylint: disable=global-statement

        warnings = set()
        errors = set()
        info = set()

        type_string = None
        if input_file.lower().endswith("mxd"):
            type_string = "MXD"
        elif input_file.lower().endswith("mxt"):
            type_string = "MXT"
        elif input_file.lower().endswith("sxd"):
            type_string = "SXD"
        elif input_file.lower().endswith("pmf"):
            type_string = "PMF"
        elif input_file.lower().endswith("3dd"):
            type_string = "ArcGlobe Document"

        if not type_string:
            return False

        if type_string in ("MXD", "MXT") and use_warnings:
            res = iface.newProject(True)
            if res is None:
                # old api (pre 3.10.1)
                if QgsProject.instance().isDirty():
                    # user opted to cancel, return
                    return True
            elif not res:
                # creating new project was cancelled
                return True

        with open(input_file, "rb") as f:
            stream = None
            try:
                if type_string in ("MXD", "MXT"):
                    obj = MapDocument(f, False, tolerant=True, read_layouts=True)
                else:
                    stream = Stream(f, False, force_layer=True, offset=-1)
                    stream.allow_shortcuts = True
                    obj = stream.read_object()

            except EmptyDocumentException:
                iface.messageBar().pushCritical(
                    "Convert {}".format(type_string), "File is empty or corrupt"
                )
                return True
            except DocumentTypeException:
                iface.messageBar().pushCritical(
                    "Convert {}".format(type_string),
                    "File is corrupt or not an {}".format(type_string),
                )
                return True
            except RequiresLicenseException as e:
                iface.messageBar().pushCritical(
                    "Convert {}".format(type_string),
                    "{}. Please see https://north-road.com/slyr/ for details".format(
                        type_string
                    ),
                )
                return True

            def unsupported_object_callback(msg, level=Context.WARNING):
                if level == Context.WARNING:
                    warnings.add(msg)
                elif level == Context.CRITICAL:
                    errors.add(msg)
                elif level == Context.INFO:
                    info.add(msg)

            conversion_context = Context()
            if isinstance(obj, MapDocument) and obj.original_path:
                conversion_context.original_path = PureWindowsPath(
                    obj.original_path
                ).parent

            conversion_context.project = QgsProject.instance()
            conversion_context.unsupported_object_callback = unsupported_object_callback

            blocker = None
            if isinstance(obj, MapDocument):
                # yuck
                blocker = QgsProjectDirtyBlocker(QgsProject.instance())

                prev_setting = iface.layerTreeCanvasBridge().autoSetupOnFirstLayer()
                iface.layerTreeCanvasBridge().setAutoSetupOnFirstLayer(False)

                if Qgis.QGIS_VERSION_INT >= 33500:
                    iface.blockActiveLayerChanges(True)
                ProjectConverter.convert_target_project(
                    QgsProject.instance(),
                    input_file,
                    obj,
                    conversion_context,
                    canvas=iface.mapCanvas(),
                )
                if Qgis.QGIS_VERSION_INT >= 33500:
                    iface.blockActiveLayerChanges(False)

                def post_steps():
                    global blocker  # pylint: disable=global-statement
                    iface.layerTreeCanvasBridge().setAutoSetupOnFirstLayer(prev_setting)
                    del blocker
                    blocker = None

                QTimer.singleShot(500, lambda: post_steps)

            elif isinstance(obj, Map):
                # yuck
                prev_setting = iface.layerTreeCanvasBridge().autoSetupOnFirstLayer()
                iface.layerTreeCanvasBridge().setAutoSetupOnFirstLayer(False)

                if Qgis.QGIS_VERSION_INT >= 33500:
                    iface.blockActiveLayerChanges(True)
                ProjectConverter.update_project(
                    QgsProject.instance(),
                    input_file,
                    obj,
                    conversion_context,
                    multiframes=stream.data_frame_count > 1,
                    canvas=iface.mapCanvas(),
                )
                if Qgis.QGIS_VERSION_INT >= 33500:
                    iface.blockActiveLayerChanges(False)

                if stream.data_frame_count > 1:
                    for _ in range(1, stream.data_frame_count):
                        obj = stream.read_object()
                        if isinstance(obj, Map):
                            if Qgis.QGIS_VERSION_INT >= 33500:
                                iface.blockActiveLayerChanges(True)
                            ProjectConverter.update_project(
                                QgsProject.instance(),
                                input_file,
                                obj,
                                conversion_context,
                                multiframes=True,
                            )
                            if Qgis.QGIS_VERSION_INT >= 33500:
                                iface.blockActiveLayerChanges(False)
                        else:
                            assert False, "unexpected object type"
                QTimer.singleShot(
                    500,
                    lambda: iface.layerTreeCanvasBridge().setAutoSetupOnFirstLayer(
                        prev_setting
                    ),
                )
            else:
                return False

        try:
            QgsProject.instance().setOriginalPath(input_file)
        except AttributeError:
            pass

        if warnings or errors or info:
            message = ""
            title = ""
            level = None

            if errors:
                message = "<p>The following errors were generated while converting the {} file:</p>".format(
                    type_string
                )
                message += "<ul>"
                for w in errors:
                    message += "<li>{}</li>".format(
                        html.escape(w).replace("\n", "<br>")
                    )
                message += "</ul>"
                title = "{} could not be completely converted".format(type_string)
                level = Qgis.MessageLevel.Critical
            if warnings:
                if message:
                    message += "<p>Additionally, some warnings were generated:</p>"
                else:
                    message += "<p>The following warnings were generated while converting the {} file:</p>".format(
                        type_string
                    )
                message += "<ul>"
                for w in warnings:
                    message += "<li>{}</li>".format(
                        html.escape(w).replace("\n", "<br>")
                    )
                message += "</ul>"
                if not title:
                    title = "Some warnings were encountered while converting {}".format(
                        type_string
                    )
                if level is None:
                    level = Qgis.MessageLevel.Warning

            if info:
                if message:
                    message += (
                        "<p>Additionally, some extra messages were generated:</p>"
                    )
                else:
                    message += "<p>The following information messages were generated converting the {} file:</p>".format(
                        type_string
                    )
                message += "<ul>"
                for w in info:
                    message += "<li>{}</li>".format(
                        html.escape(w).replace("\n", "<br>")
                    )
                message += "</ul>"
                if not title:
                    title = "Some messages were generated while converting {}".format(
                        type_string
                    )
                if level is None:
                    level = Qgis.MessageLevel.Info

            BrowserUtils.show_warning(
                title, "Convert {}".format(type_string), message, level=level
            )

        return True

    def customUriProviderKey(self):  # pylint: disable=missing-docstring
        return "esri_mxd"

    def handleCustomUriDrop(self, uri):  # pylint: disable=missing-docstring
        path = uri.uri
        self.open_mxd(path)


class EsriMxdItem(QgsDataItem):
    """
    Data item for .mxd files
    """

    def __init__(self, parent, name, path):
        super().__init__(QgsDataItem.Type.Custom, parent, name, path)
        self.setState(QgsDataItem.State.Populated)  # no children
        self.setToolTip(QDir.toNativeSeparators(path))

    def hasDragEnabled(self):  # pylint: disable=missing-docstring
        return True

    def handleDoubleClick(self):  # pylint: disable=missing-docstring
        self.open_mxd()
        return True

    def icon(self):  # pylint: disable=missing-docstring
        return GuiUtils.get_icon("mxd.svg")

    def mimeUri(self):  # pylint: disable=missing-docstring
        u = QgsMimeDataUtils.Uri()
        u.layerType = "custom"
        u.providerKey = "esri_mxd"
        u.name = self.name()
        u.uri = self.path()
        return u

    def mimeUris(self):  # pylint: disable=missing-docstring
        return [self.mimeUri()]

    def paramWidget(self):  # pylint: disable=missing-docstring
        widget = MxdBrowserWidget(self.path())
        return widget

    def open_mxd(self):
        """
        Handles opening .mxd files
        """

        MxdDropHandler.open_mxd(self.path())
        return True

    def actions(self, parent):  # pylint: disable=missing-docstring
        if self.path().lower().endswith("mxd"):
            action_text = QCoreApplication.translate("SLYR", "&Open MXD…")
        elif self.path().lower().endswith("mxt"):
            action_text = QCoreApplication.translate("SLYR", "&Open MXT…")
        elif self.path().lower().endswith("sxd"):
            action_text = QCoreApplication.translate("SLYR", "&Open ArcScene SXD…")
        elif self.path().lower().endswith("pmf"):
            action_text = QCoreApplication.translate("SLYR", "&Open PMF…")
        elif self.path().lower().endswith("3dd"):
            action_text = QCoreApplication.translate("SLYR", "&Open 3dd…")
        open_action = QAction(action_text, parent)
        open_action.triggered.connect(self.open_mxd)
        return [open_action]


if QgsCustomProjectOpenHandler is not None:

    class MxdProjectOpenHandler(QgsCustomProjectOpenHandler):
        """
        Custom project open handler for MXD documents
        """

        def filters(self):  # pylint: disable=missing-function-docstring
            return [
                "ArcGIS MXD Documents (*.mxd *.MXD)",
                "ArcGIS MXT Templates (*.mxt *.MXT)",
                "ArcReader Published Map Files (*.pmf *.PMF)",
                "ArcScene SXD Documents (*.sxd *.SXD)",
            ]

        def handleProjectOpen(self, file):  # pylint: disable=missing-function-docstring
            return MxdDropHandler.open_mxd(file)

        def createDocumentThumbnailAfterOpen(self):  # pylint: disable=missing-function-docstring
            return True

        def icon(self):  # pylint: disable=missing-function-docstring
            return GuiUtils.get_icon("mxd.svg")
else:
    MxdProjectOpenHandler = None
