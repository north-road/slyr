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

from qgis.PyQt.QtGui import QColor
from slyr_community.parser.objects.colors import CmykColor


class ColorConverter:

    @staticmethod
    def color_to_qcolor(color):
        """
        Converts a symbol color to a QColor
        """
        if color is None:
            return QColor()

        if isinstance(color, CmykColor):
            # CMYK color
            c = QColor.fromCmykF(color.cyan / 100, color.magenta / 100, color.yellow / 100, color.black / 100)
            if color.is_null:
                c.setAlpha(0)
            return c

        return QColor(color.red, color.green, color.blue, 0 if color.is_null else 255)
