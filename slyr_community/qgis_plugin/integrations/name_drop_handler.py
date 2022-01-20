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
Handles dropping ESRI name mime data
"""

from qgis.core import (
    Qgis
)
from qgis.gui import (
    QgsCustomDropHandler
)

from .browser_utils import BrowserUtils


class NameDropHandler(QgsCustomDropHandler):
    """
    Handles dropping ESRI name mime data
    """

    DATA_TYPE = 'application/x-qt-windows-mime;value="ESRI Names"'

    def customUriProviderKey(self):  # pylint: disable=missing-function-docstring
        return 'esri_names'

    def canHandleMimeData(self, data):  # pylint: disable=missing-function-docstring
        return data.hasFormat(NameDropHandler.DATA_TYPE)

    def handleMimeDataV2(self, data):  # pylint: disable=missing-function-docstring
        if data.hasFormat(NameDropHandler.DATA_TYPE):
            message = '<p>This functionality requires the licensed version of SLYR. Please see <a href="https://north-road.com/slyr/">here</a> for details.</p>'
            BrowserUtils.show_warning('Could not handle item drop', '', message,
                                      level=Qgis.Critical)
            return True
        return False
