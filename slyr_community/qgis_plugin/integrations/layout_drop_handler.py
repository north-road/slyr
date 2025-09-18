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
Handles pasting layout elements from ArcMap
"""

from qgis.core import Qgis
from qgis.gui import QgsLayoutCustomDropHandler

from .browser_utils import BrowserUtils


class LayoutDropHandler(QgsLayoutCustomDropHandler):
    """
    Handles pasting layout elements from ArcMap
    """

    def __init__(self, parent=None):  # pylint: disable=useless-super-delegation
        super().__init__(parent)

    def handlePaste(
        self,  # pylint: disable=missing-function-docstring,unused-argument
        designer_iface,  # pylint: disable=unused-argument
        pastePoint,  # pylint: disable=unused-argument
        data,
    ):  # pylint: disable=unused-argument
        if (
            'application/x-qt-windows-mime;value="Esri Graphics List"'
            not in data.formats()
        ):
            return False, []

        message = '<p>Pasting page layout elements requires the licensed version of SLYR. Please see <a href="https://north-road.com/slyr/">here</a> for details.</p>'
        BrowserUtils.show_warning(
            "Could not paste all elements",
            "Paste Elements",
            message,
            level=Qgis.Critical,
            message_bar=designer_iface.messageBar(),
        )
        return True, []
