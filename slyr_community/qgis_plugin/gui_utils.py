# -*- coding: utf-8 -*-

# /***************************************************************************
# gui_utils.py
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
GUI Utilities
"""

import os

from qgis.PyQt.QtCore import QThread, QCoreApplication
from qgis.PyQt.QtGui import QIcon

from qgis.core import QgsWkbTypes, QgsMapLayer, QgsMimeDataUtils


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
    def get_valid_mime_uri(layer_name, uri, wkb_type):
        """
        Gross method to force a valid layer path, only used for very old QGIS versions
        """
        if QgsWkbTypes.geometryType(wkb_type) == QgsWkbTypes.NullGeometry:
            layer_type = QgsMapLayer.RasterLayer
        else:
            layer_type = QgsMapLayer.VectorLayer

        if QThread.currentThread() == QCoreApplication.instance().thread():
            from .datasourceselectdialog import DataSourceSelectDialog  # pylint: disable=import-outside-toplevel

            dlg = DataSourceSelectDialog(
                layer_name=layer_name, original_uri=uri, layer_type=layer_type
            )
            if dlg.exec_():
                return dlg.uri

        # use default dummy path - QGIS 3.4 will crash on invalid layer sources otherwise
        uri = QgsMimeDataUtils.Uri()
        if QgsWkbTypes.geometryType(wkb_type) == QgsWkbTypes.PointGeometry:
            file = "dummy_points.shp"
        elif QgsWkbTypes.geometryType(wkb_type) == QgsWkbTypes.LineGeometry:
            file = "dummy_lines.shp"
        elif QgsWkbTypes.geometryType(wkb_type) == QgsWkbTypes.PolygonGeometry:
            file = "dummy_polygon.shp"
        elif QgsWkbTypes.geometryType(wkb_type) == QgsWkbTypes.NullGeometry:
            file = "dummy_raster.tif"
        else:
            # ???
            file = "dummy_points.shp"

        path = os.path.dirname(os.path.abspath(__file__))
        uri.uri = os.path.realpath(os.path.join(path, "..", "..", file)).replace(
            "\\", "/"
        )
        uri.providerKey = "ogr"
        return uri
