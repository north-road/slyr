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
import os
import re
from pathlib import Path
from typing import Optional

from qgis.PyQt.QtCore import Qt, QPointF, QVariant
from qgis.core import (
    QgsField,
    QgsFields,
    QgsMemoryProviderUtils,
    QgsFeature
)

from ..bintools.extractor import Extractor


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
    def convert_mdb_table_to_memory_layer(file_path: str, table_name: str):
        """
        Extracts the contents of a non-spatial table from a MDB to a memory layer
        :param file_path: path to .mdb file
        :param table_name: table name to extract
        """
        rows = Extractor.extract_non_spatial_table_from_mdb(file_path, table_name)

        header = rows[0]
        rows = rows[1:]

        fields = QgsFields()
        for idx, h in enumerate(header):
            # sniff first row
            if isinstance(rows[0][idx], float):
                field_type = QVariant.Double
            elif isinstance(rows[0][idx], int):
                field_type = QVariant.Int
            else:
                field_type = QVariant.String

            fields.append(QgsField(h, field_type))

        layer = QgsMemoryProviderUtils.createMemoryLayer(table_name, fields)

        for row in rows:
            f = QgsFeature()
            f.initAttributes(len(row))
            f.setAttributes(row)
            layer.dataProvider().addFeature(f)

        return layer

    @staticmethod
    def path_insensitive(path):
        """
        Recursive part of path_insensitive to do the work.
        """
        try:
            return ConversionUtils._path_insensitive(path) or path
        except PermissionError:
            return path

    @staticmethod
    def _path_insensitive(path) -> Optional[str]:  # pylint: disable=too-many-return-statements
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

        if not base:
            return None

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

    @staticmethod
    def is_absolute_path(path: str) -> bool:
        """
        Returns True if a path is an absolute path
        """
        if path.startswith('.'):
            return False

        if path.startswith(r'//'):
            return True

        return bool(re.match(r'^\w:', path))

    @staticmethod
    def get_absolute_path(path: str, base: str) -> str:
        """
        Converts a path to an absolute path, in a case insensitive way
        """

        path = path.replace('\\', '/')

        if ConversionUtils.is_absolute_path(path):
            return ConversionUtils.path_insensitive(path)

        res = ConversionUtils.path_insensitive('{}/{}'.format(base, path))
        res = res.replace('/./', '/')
        return res
