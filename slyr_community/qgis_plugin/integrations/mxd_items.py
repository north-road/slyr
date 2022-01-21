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
Browser and app integrations for MXD/PMF/SXD/MXT file integration with QGIS
"""

from qgis.PyQt.QtCore import QDir, QCoreApplication
from qgis.PyQt.QtWidgets import (
    QAction)
from qgis.core import (
    Qgis,
    QgsDataItem,
    QgsMimeDataUtils
)
from qgis.gui import (
    QgsCustomDropHandler
)
from qgis.utils import iface

from .browser_utils import BrowserUtils
from ..gui_utils import GuiUtils

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
        if not (file.lower().endswith('.mxd') or file.lower().endswith('.sxd') or file.lower().endswith(
                '.pmf') or file.lower().endswith('.3dd') or file.lower().endswith('.mxt')):
            return False
        return self.open_mxd(file)

    @staticmethod
    def open_mxd(input_file,  # pylint:disable=too-many-locals,too-many-return-statements,too-many-branches,too-many-statements
                 use_warnings=True):  # pylint:disable=unused-argument
        """
        Opens an MXD file in the current project
        """
        type_string = None
        if input_file.lower().endswith('mxd'):
            type_string = 'MXD'
        elif input_file.lower().endswith('mxt'):
            type_string = 'MXT'
        elif input_file.lower().endswith('sxd'):
            type_string = 'SXD'
        elif input_file.lower().endswith('pmf'):
            type_string = 'PMF'
        elif input_file.lower().endswith('3dd'):
            type_string = 'ArcGlobe Document'

        if not type_string:
            return False

        message = '<p>This functionality requires the licensed version of SLYR. Please see <a href="https://north-road.com/slyr/">here</a> for details.</p>'
        BrowserUtils.show_warning('Licensed version required', 'Convert MXD', message,
                                  level=Qgis.Critical, message_bar=iface.messageBar())
        return True

    def customUriProviderKey(self):  # pylint: disable=missing-docstring
        return 'esri_mxd'

    def handleCustomUriDrop(self, uri):  # pylint: disable=missing-docstring
        path = uri.uri
        self.open_mxd(path)


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

    def mimeUris(self):  # pylint: disable=missing-docstring
        return [self.mimeUri()]

    def open_mxd(self):
        """
        Handles opening .mxd files
        """
        MxdDropHandler.open_mxd(self.path())
        return True

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


if QgsCustomProjectOpenHandler is not None:
    class MxdProjectOpenHandler(QgsCustomProjectOpenHandler):
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
else:
    MxdProjectOpenHandler = None
