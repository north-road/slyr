"""
GUI Utilities
"""

# /***************************************************************************
#  *                                                                         *
#  *   This program is free software; you can redistribute it and/or modify  *
#  *   it under the terms of the GNU General Public License as published by  *
#  *   the Free Software Foundation; either version 2 of the License, or     *
#  *   (at your option) any later version.                                   *
#  *                                                                         *
#  ***************************************************************************/

import os
from typing import Optional

from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QMenu


from qgis.utils import iface


class GuiUtils:
    """
    Utilities for GUI plugin components
    """

    @staticmethod
    def get_icon(icon: str):
        """
        Returns a plugin icon
        :param icon: icon name (svg file name)
        :return: QIcon
        """
        path = GuiUtils.get_icon_path(icon)
        if not path:
            return QIcon()

        return QIcon(path)

    @staticmethod
    def get_icon_path(icon: str):
        """
        Returns a plugin icon path
        :param icon: icon name (svg file name)
        :return: icon path
        """
        path = os.path.join(os.path.dirname(__file__), "..", "images", icon)
        if not os.path.exists(path):
            return ""

        return path

    @staticmethod
    def get_ui_path(file: str):
        """
        Returns a UI file path
        :param file: UI file name
        :return: full UI file path
        """
        path = os.path.join(os.path.dirname(__file__), "ui", file)
        if not os.path.exists(path):
            return ""

        return path

    @staticmethod
    def get_project_import_export_menu() -> Optional[QMenu]:
        """
        Returns the application Project - Import/Export sub menu
        """
        try:
            # requires QGIS 3.30+
            return iface.projectImportExportMenu()
        except AttributeError:
            pass

        project_menu = iface.projectMenu()
        matches = [
            m for m in project_menu.children() if m.objectName() == "menuImport_Export"
        ]
        if matches:
            return matches[0]

        return None
