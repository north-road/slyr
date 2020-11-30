#!/usr/bin/env python

# /***************************************************************************
# context.py
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
Conversion context
"""

import os
import tempfile

from qgis.PyQt.QtCore import (
    QSettings,
    QDir
)
from qgis.core import (
    Qgis,
    QgsUnitTypes
)


class Context:
    """
    Symbol conversion context
    """

    WARNING = 'WARNING'
    CRITICAL = 'CRITICAL'

    def __init__(self):
        s = QSettings()
        self.layer_name = ''
        self.file_name = ''
        self.dataset_name = ''
        self.symbol_name = ''
        self.picture_folder = s.value('/plugins/slyr/picture_store_folder', '')
        self.temporary_picture_folder = ''
        self.style_folder = ''
        self.embed_pictures = int(s.value('/plugins/slyr/embed_pictures', Qgis.QGIS_VERSION_INT >= 30600))
        self.convert_fonts = int(s.value('/plugins/slyr/convert_font_to_svg', 0))
        self.relative_paths = int(s.value('/plugins/slyr/store_relative', 0))
        self.units = int(s.value('/plugins/slyr/symbol_units', int(QgsUnitTypes.RenderPoints)))
        self.apply_conversion_tweaks = int(s.value('/plugins/slyr/apply_tweaks', 1))
        self.inkscape_path = s.value('/plugins/slyr/inkscape_path', 'inkscape')
        self.convert_annotations = int(s.value('/plugins/slyr/enable_annotations', 0))
        self.convert_layouts = int(s.value('/plugins/slyr/convert_layouts', 1))
        self.unsupported_object_callback = None
        self.invalid_layer_resolver = None
        self.warned_crs_definitions = set()
        self.layer_type_hint = None
        self.ignore_online_sources = False  # debugging only!

    def get_picture_store_folder(self):
        """
        Returns the destination folder for converted pictures
        """
        if self.picture_folder:
            if not os.path.exists(self.picture_folder):
                os.makedirs(self.picture_folder)
            return self.picture_folder

        if not self.temporary_picture_folder:
            self.temporary_picture_folder = tempfile.gettempdir()
            if not os.path.exists(self.temporary_picture_folder):
                os.makedirs(self.temporary_picture_folder)
        return self.temporary_picture_folder

    def convert_size(self, size: float) -> float:  # pylint: disable=inconsistent-return-statements
        """
        Returns a size converted to the desired symbol units
        """
        if self.units == QgsUnitTypes.RenderPoints:
            return size
        elif self.units == QgsUnitTypes.RenderMillimeters:
            return size * 0.352778
        else:
            assert False, 'Unsupported unit type {}'.format(self.units)

    def convert_path(self, path: str) -> str:
        """
        Converts an absolute path for storage in the symbol
        """
        if not self.relative_paths:
            return path

        return QDir(self.style_folder).relativeFilePath(path)

    def fix_line_width(self, size) -> float:
        """
        Applies line width tweaks to better represent original ESRI symbols
        """
        if not self.apply_conversion_tweaks:
            return size

        if size <= .4:
            # ESRI renders this closer to a "hairline" width in QGIS land
            return 0
        return size
