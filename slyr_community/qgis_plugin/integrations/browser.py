"""
Browser and app integrations for LYR/STYLE file integration with QGIS
"""

# /***************************************************************************
#  *                                                                         *
#  *   This program is free software; you can redistribute it and/or modify  *
#  *   it under the terms of the GNU General Public License as published by  *
#  *   the Free Software Foundation; either version 2 of the License, or     *
#  *   (at your option) any later version.                                   *
#  *                                                                         *
#  ***************************************************************************/

from qgis.PyQt.QtCore import QFileInfo
from qgis.core import QgsDataItemProvider, QgsDataProvider

from .lyr_items import EsriLyrItem

from .mxd_items import EsriMxdItem
from .style_items import EsriStyleItem


class SlyrDataItemProvider(QgsDataItemProvider):
    """
    Data item provider for .style/.lyr files
    """

    def name(self):  # pylint: disable=missing-docstring
        return "slyr"

    def capabilities(self):  # pylint: disable=missing-docstring
        return QgsDataProvider.DataCapability.File

    def createDataItem(self, path, parentItem):  # pylint: disable=missing-docstring
        file_info = QFileInfo(path)

        if file_info.suffix().lower() == "style":
            return EsriStyleItem(parentItem, file_info.fileName(), path)
        elif file_info.suffix().lower() in ("lyr",):
            return EsriLyrItem(parentItem, file_info.fileName(), path)
        elif file_info.suffix().lower() in ("mxd",):
            return EsriMxdItem(parentItem, file_info.fileName(), path)
        return None
