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
import re
import tempfile
import base64
from pathlib import WindowsPath, Path
from math import cos, sin, asin, sqrt, radians

from typing import Optional, Dict, List, Union

from qgis.PyQt.QtCore import (
    QSettings,
    QDir
)
from qgis.core import (
    Qgis,
    QgsUnitTypes,
    QgsSymbol,
    QgsProject,
    QgsReferencedRectangle
)

from ..parser.exceptions import NotImplementedException


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
        self.current_symbol = None
        self.current_symbol_layer = None
        self.picture_folder = s.value('/plugins/slyr/picture_store_folder', '')
        self.temporary_picture_folder = ''
        self.style_folder = ''
        self.embed_pictures = int(s.value('/plugins/slyr/embed_pictures', Qgis.QGIS_VERSION_INT >= 30600))
        self.convert_fonts = int(s.value('/plugins/slyr/convert_font_to_svg', 0))
        self.relative_paths = int(s.value('/plugins/slyr/store_relative', 0))
        try:
            unit = s.value('/plugins/slyr/symbol_units', int(QgsUnitTypes.RenderPoints), int)
            if unit is None:
                unit = QgsUnitTypes.RenderPoints
            else:
                unit = QgsUnitTypes.RenderUnit(unit)
        except TypeError:
            unit = QgsUnitTypes.RenderPoints
        except AttributeError:
            unit = QgsUnitTypes.RenderPoints

        self.units = unit
        self.apply_conversion_tweaks = int(s.value('/plugins/slyr/apply_tweaks', 1))
        self.inkscape_path = s.value('/plugins/slyr/inkscape_path', 'inkscape')
        self.convert_esri_fonts_to_simple_markers = int(s.value('/plugins/slyr/convert_fonts_to_simple_markers', 1))

        self.sde_primary_key: str = s.value('/plugins/slyr/sde_primary_key', 'OBJECTID')
        self.sde_table_name_conversion: str = s.value('/plugins/slyr/sde_name_conversion', 'unchanged')

        self.unsupported_object_callback = None
        self.invalid_layer_resolver = None
        self.warned_crs_definitions = set()
        self.layer_type_hint = None
        self.ignore_online_sources = False  # debugging only!
        self.main_layer_name = None
        self.use_real_world_units = False
        self.global_cim_effects = []
        self.frame_crs = None

        self.stable_ids = False
        self.stable_id_counter = 0

        self.symbol_type_hint: Optional[QgsSymbol.SymbolType] = None

        self.used_geometric_effect_which_flips_orientation = False

        self.selection_sets: Dict[str, List] = {}

        self.symbol_layer_output_to_input_index_map = {}
        self.final_symbol_layer_output_to_input_index_map = {}

        # associated project
        self.project: Optional[QgsProject] = None

        # folder for destination file
        self.destination_path: Optional[Path] = None

        self.approx_map_area: Optional[QgsReferencedRectangle] = None

    def push_warning(self, warning: str, level: Optional[str]=None):
        """
        Pushes a warning to the context
        """
        if not level:
            level = Context.WARNING

        if not self.unsupported_object_callback:
            return

        if self.layer_name:
            self.unsupported_object_callback(
                '{}: {}'.format(
                    self.layer_name,
                    warning),
                level=level)
        elif self.symbol_name:
            self.unsupported_object_callback(
                '{}: {}'.format(
                    self.symbol_name,
                    warning),
                level=level)
        else:
            self.unsupported_object_callback(
                warning,
                level=level)

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

    def convert_size_to_points(self, size: float, units) -> Optional[float]:
        """
        Converts a size to points
        """
        if units == QgsUnitTypes.RenderPoints:
            return size
        elif units == QgsUnitTypes.RenderMillimeters:
            return size / 0.352778
        elif units == QgsUnitTypes.RenderInches:
            return size * 72
        elif units == QgsUnitTypes.RenderPixels:
            if self.unsupported_object_callback:
                self.unsupported_object_callback(
                    '{} ArcGIS Pro does not support pixel units'.format(
                        self.symbol_name),
                    level=Context.WARNING)
            return size / 96 * 72  # assume 96 dpi
        elif units == QgsUnitTypes.RenderMetersInMapUnits:
            return size
        elif units in (QgsUnitTypes.RenderMapUnits,
                       QgsUnitTypes.RenderPercentage):
            unit_name = QgsUnitTypes.toString(units)
            if self.unsupported_object_callback:
                self.unsupported_object_callback(
                    '{} ArcGIS Pro does not support {} units'.format(
                        self.symbol_name, unit_name),
                    level=Context.WARNING)
            return None

        raise NotImplementedException('Converting units of type {} is not supported'.format(units))

    def convert_map_units_to_meters(self, size_map_units: float):
        """
        Converts map units to approximate meters
        """
        if self.approx_map_area:
            if self.approx_map_area.crs().mapUnits() == QgsUnitTypes.DistanceDegrees\
                    or not self.approx_map_area.crs().isValid():
                center = self.approx_map_area.center()

                lon2 = 1
                lat = center.y()
                lat, dlon = map(radians, [lat, lon2])
                # haversine formula
                a = cos(lat) * cos(lat) * sin(
                    dlon / 2) ** 2
                c = 2 * asin(sqrt(a))
                conversion_factor = 6371000 * c
            else:
                conversion_factor = QgsUnitTypes.fromUnitToUnitFactor(
                    self.approx_map_area.crs().mapUnits(),
                    QgsUnitTypes.DistanceMeters)
        else:
            conversion_factor = QgsUnitTypes.fromUnitToUnitFactor(
                QgsUnitTypes.DistanceDegrees, QgsUnitTypes.DistanceMeters)

        return size_map_units * conversion_factor

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

    @staticmethod
    def find_relative_path(path: str, diverge_path: Union[str, Path]) -> Union[bool, str]:
        """
        Returns a relative path that redirects to the first parameter
        If the paths are not relative, False is returned
        If both paths are the same, '.' is returned

        e.g. 'path/example' and 'path/test' would return './example/',
        as the path redirects to the first path
        """
        if isinstance(diverge_path, Path):
            diverge_path = str(diverge_path)

        if path == diverge_path:
            return '.'

        output = os.path.relpath(path, diverge_path)
        if output == '.':
            return '.'
        elif path in output:
            return False
        return output

    def convert_dataset_path(self, path: Union[str, Path]) -> str:
        """
        Converts a dataset's path for writing to ArcGIS formats, using relative paths if possible
        """
        if isinstance(path, Path):
            path = str(path)

        is_rel_path = False
        if self.destination_path is None:
            converted_path = path
        else:
            new_path = Context.find_relative_path(path, self.destination_path)
            if new_path is False:
                converted_path = path
                is_rel_path = False
            else:
                is_rel_path = True
                converted_path = new_path

        if converted_path == '':
            converted_path = '.'

        if is_rel_path and not converted_path.startswith(".") and not converted_path.startswith(".."):
            converted_path = ".\\" + converted_path

        try:
            return str(WindowsPath(converted_path))
        except NotImplementedError:
            return converted_path.replace('/', '\\')
