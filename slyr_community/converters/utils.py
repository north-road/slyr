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

from typing import Optional
import math
import os
from pathlib import Path

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

    @staticmethod
    def path_insensitive(path) -> Optional[str]:
        """
        Recursive part of path_insensitive to do the work.
        """
        return ConversionUtils._path_insensitive(path) or path

    @staticmethod
    def _path_insensitive(path) -> Optional[str]:
        """
        Recursive part of path_insensitive to do the work.
        """

        if path == '' or os.path.exists(path):
            return Path(path).resolve().as_posix() if path else path

        path = Path(path).resolve().as_posix()

        base = os.path.basename(path)  # may be a directory or a file
        dirname = os.path.dirname(path)

        suffix = ''
        if not base:  # dir ends with a slash?
            if len(dirname) < len(path):
                suffix = path[:len(path) - len(dirname)]

            base = os.path.basename(dirname)
            dirname = os.path.dirname(dirname)

        if not os.path.exists(dirname):
            dirname = ConversionUtils._path_insensitive(dirname)
            if not dirname:
                return None

        # at this point, the directory exists but not the file

        try:  # we are expecting dirname to be a directory, but it could be a file
            files = os.listdir(dirname)
        except OSError:
            return None

        base_low = base.lower()
        try:
            base_final = next(fl for fl in files if fl.lower() == base_low)
        except StopIteration:
            return None

        if base_final:
            return Path(os.path.join(dirname, base_final) + suffix).as_posix()
        else:
            return None
