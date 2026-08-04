"""
Bookmark converter
"""

# /***************************************************************************
#  *                                                                         *
#  *   This program is free software; you can redistribute it and/or modify  *
#  *   it under the terms of the GNU General Public License as published by  *
#  *   the Free Software Foundation; either version 2 of the License, or     *
#  *   (at your option) any later version.                                   *
#  *                                                                         *
#  ***************************************************************************/

from qgis.core import (
    QgsRectangle,
    QgsReferencedRectangle,
    QgsBookmark,
)

from .context import Context
from .crs import CrsConverter


class BookmarkConverter:
    @staticmethod
    def convert_bookmark(name, extent, context: Context):
        bookmark = QgsBookmark()
        bookmark.setName(name)
        crs = CrsConverter.convert_crs(extent.crs, context)
        rect = QgsRectangle(extent.x_min, extent.y_min, extent.x_max, extent.y_max)

        bookmark.setExtent(QgsReferencedRectangle(rect, crs))
        return bookmark
