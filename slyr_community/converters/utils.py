#!/usr/bin/env python

# /***************************************************************************
# utils.py
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
Conversion utilities
"""

import math
from qgis.PyQt.QtCore import Qt, QPointF


class ConversionUtils:
    """
    Conversion utilities
    """

    @staticmethod
    def convert_angle(angle: float) -> float:
        """
        Converts an ESRI angle (counter-clockwise) to a QGIS angle (clockwise)
        """
        a = 360 - angle
        if a > 180:
            # instead of "359", use "-1"
            a -= 360
        return a

    @staticmethod
    def adjust_offset_for_rotation(offset, rotation):
        """
        Adjusts marker offset to account for rotation
        """
        angle = -math.radians(rotation)
        return QPointF(offset.x() * math.cos(angle) - offset.y() * math.sin(angle),
                       offset.x() * math.sin(angle) + offset.y() * math.cos(angle))

    @staticmethod
    def symbol_pen_to_qpenstyle(style):
        """
        Converts a symbol pen style to a QPenStyle
        """
        types = {
            'solid': Qt.SolidLine,
            'dashed': Qt.DashLine,
            'dotted': Qt.DotLine,
            'dash dot': Qt.DashDotLine,
            'dash dot dot': Qt.DashDotDotLine,
            'null': Qt.NoPen
        }
        return types[style]

    @staticmethod
    def symbol_pen_to_qpencapstyle(style):
        """
        Converts a symbol pen cap to a QPenCapStyle
        """
        types = {
            'butt': Qt.FlatCap,
            'round': Qt.RoundCap,
            'square': Qt.SquareCap
        }
        return types[style]

    @staticmethod
    def symbol_pen_to_qpenjoinstyle(style):
        """
        Converts a symbol pen join to a QPenJoinStyle
        """
        types = {
            'miter': Qt.MiterJoin,
            'round': Qt.RoundJoin,
            'bevel': Qt.BevelJoin
        }
        return types[style]
