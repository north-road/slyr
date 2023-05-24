#!/usr/bin/env python

# /***************************************************************************
# crs.py
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
Coordinate reference system conversion
"""
import re

from qgis.core import (
    QgsCoordinateReferenceSystem
)
from ..parser.objects.unknown_coordinate_system import UnknownCoordinateSystem
from .context import Context


class CrsConverter:
    """
    Converts CRS to QgsCoordinateReferenceSystem
    """

    @staticmethod
    def convert_crs(crs, context: Context):
        """
        Converts CRS to QgsCoordinateReferenceSystem
        """
        if not crs:
            return QgsCoordinateReferenceSystem()

        if isinstance(crs, UnknownCoordinateSystem):
            return QgsCoordinateReferenceSystem()

        wkt = crs.wkt
        try:
            from qgis.core import QgsProjUtils  # pylint: disable=import-outside-toplevel
            if QgsProjUtils.projVersionMajor() < 7 or (QgsProjUtils.projVersionMajor() == 7 and QgsProjUtils.projVersionMinor() < 2):
                # a bit of a hack, but in place until Proj 7.2 which can handle "Local" projection method...
                wkt = wkt.replace('PROJECTION["Local"]', 'PROJECTION["Orthographic"]')
        except ImportError:
            # we just assume older qgis releases are also on older proj releases...
            wkt = wkt.replace('PROJECTION["Local"]', 'PROJECTION["Orthographic"]')

        res = QgsCoordinateReferenceSystem(wkt)

        if not res.isValid():
            # try replacing "EPSG" code with "ESRI"
            wkt = re.sub(r'AUTHORITY\s*\[\s*"?\s*EPSG\s*"?\s*,\s*"?(\d+)\s*"?\s*(]+)$',
                         'AUTHORITY["ESRI","\\1"\\2', wkt)
            res = QgsCoordinateReferenceSystem(wkt)

        if not res.isValid() and context.unsupported_object_callback and crs.wkt not in context.warned_crs_definitions:
            context.unsupported_object_callback('Could not convert CRS with WKT: {}'.format(crs.wkt),
                                                level=Context.WARNING)
            context.warned_crs_definitions.add(crs.wkt)
        return res
