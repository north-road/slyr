#!/usr/bin/env python

# /***************************************************************************
# color.py
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
Color converter
"""

from typing import Optional

from qgis.PyQt.QtGui import QColor

from ..parser.color_parser import cielab_to_rgb2
from ..parser.objects.colors import CmykColor


class ColorConverter:
    """
    Color converter
    """

    @staticmethod
    def color_to_qcolor(color):
        """
        Converts a symbol color to a QColor
        """
        if color is None:
            return QColor(0, 0, 0, 0)

        if isinstance(color, CmykColor):
            # CMYK color
            c = QColor.fromCmykF(
                color.cyan / 100,
                color.magenta / 100,
                color.yellow / 100,
                color.black / 100,
            )
            if color.is_null:
                c.setAlpha(0)
            return c

        return QColor(color.red, color.green, color.blue, 0 if color.is_null else 255)
