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
from math import cos, sin, asin, sqrt, radians
from pathlib import WindowsPath, Path
from typing import Optional, Dict, List, Union

from qgis.PyQt.QtCore import QSettings
from qgis.core import QgsUnitTypes, QgsSymbol, QgsProject, QgsReferencedRectangle

from ..parser.exceptions import NotImplementedException


class Context:
    """
    Symbol conversion context
    """

    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

    def __init__(self):
        s = QSettings()
        self.layer_name: Optional[str] = None
        self.layout_name: Optional[str] = None
        self.element_name: Optional[str] = None
        self.symbol_name: Optional[str] = None

        self.file_name = ""

        # original path to document, if available
        self.original_path: Optional[Path] = None

        self.document_file: Optional[str] = None

        self.dataset_name = ""
        self.current_symbol = None
        self.current_symbol_layer = None
        self.picture_folder: Optional[str] = None
        self.temporary_picture_folder = ""
        self.convert_fonts = int(s.value("/plugins/slyr/convert_fonts_to_svg", 1))
        try:
            unit = s.value(
                "/plugins/slyr/symbol_units",
                int(QgsUnitTypes.RenderUnit.RenderPoints),
                int,
            )
            if unit is None:
                unit = QgsUnitTypes.RenderUnit.RenderPoints
            else:
                unit = QgsUnitTypes.RenderUnit(unit)
        except TypeError:
            unit = QgsUnitTypes.RenderUnit.RenderPoints
        except AttributeError:
            unit = QgsUnitTypes.RenderUnit.RenderPoints

        self.units = unit
        self.apply_conversion_tweaks = int(s.value("/plugins/slyr/apply_tweaks", 1))
        self.inkscape_path = s.value("/plugins/slyr/inkscape_path", "inkscape")
        self.convert_esri_fonts_to_simple_markers = int(
            s.value("/plugins/slyr/convert_fonts_to_simple_markers", 1)
        )

        self.sde_primary_key: str = s.value("/plugins/slyr/sde_primary_key", "OBJECTID")
        self.sde_table_name_conversion: str = s.value(
            "/plugins/slyr/sde_name_conversion", "unchanged"
        )

        self.unsupported_object_callback = None
        self.warned_crs_definitions = set()
        self.layer_type_hint = None
        self.ignore_online_sources = False  # debugging only!
        self.main_layer_name = None
        self.use_real_world_units = False
        self.global_cim_effects = []
        self.frame_crs = None

        self.can_place_annotations_in_main_annotation_layer = True

        self.stable_ids = False
        self.stable_id_counter = 0

        self.symbol_type_hint: Optional[QgsSymbol.SymbolType] = None

        self.used_geometric_effect_which_flips_orientation = False

        self.selection_sets: Dict[str, List] = {}

        self.symbol_layer_output_to_input_index_map = {}
        self.final_symbol_layer_output_to_input_index_map = {}

        self.map_uri_to_theme_map = {}

        # associated project
        self.project: Optional[QgsProject] = None

        # folder for destination file
        self.destination_path: Optional[Path] = None

        self.approx_map_area: Optional[QgsReferencedRectangle] = None

        self.field_to_alias_map: Dict[str, str] = {}

        self.defer_set_path_for_mdb_layers = False
        self.wrap_representation_symbols = True
        self.use_representation_overrides = True
        self.representation_override_field: Optional[str] = None
        self.representation_renderer_gdb_path: Optional[str] = None
        self.map_reference_scale: Optional[float] = None

        self.preferred_file_extension: Optional[str] = "xml"

        self.upgrade_http_to_https: bool = bool(
            int(s.value("/plugins/slyr/replace_http", 0))
        )

    def push_warning(self, warning: str, level: Optional[str] = None):
        """
        Pushes a warning to the context
        """
        if not level:
            level = Context.WARNING

        if not self.unsupported_object_callback:
            return

        if self.layout_name and self.element_name:
            self.unsupported_object_callback(
                'Page layout "{}" ({}): {}'.format(
                    self.layout_name, self.element_name, warning
                ),
                level=level,
            )
        elif self.layout_name:
            self.unsupported_object_callback(
                'Page layout "{}": {}'.format(self.layout_name, warning), level=level
            )
        elif self.element_name:
            self.unsupported_object_callback(
                'Element "{}": {}'.format(self.element_name, warning), level=level
            )
        elif self.layer_name and self.symbol_name:
            self.unsupported_object_callback(
                "{} ({}): {}".format(self.layer_name, self.symbol_name, warning),
                level=level,
            )
        elif self.layer_name:
            self.unsupported_object_callback(
                "{}: {}".format(self.layer_name, warning), level=level
            )
        elif self.symbol_name:
            self.unsupported_object_callback(
                "{}: {}".format(self.symbol_name, warning), level=level
            )
        else:
            self.unsupported_object_callback(warning, level=level)

    def embed_svgs(self) -> bool:
        """
        Returns True if SVG pictures should be embedded
        """
        return not bool(self.picture_folder)

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
        if self.units == QgsUnitTypes.RenderUnit.RenderPoints:
            return size
        elif self.units == QgsUnitTypes.RenderUnit.RenderMillimeters:
            return size * 0.352778
        else:
            assert False, "Unsupported unit type {}".format(self.units)

    def convert_size_to_points(self, size: float, units) -> Optional[float]:
        """
        Converts a size to points
        """
        if units == QgsUnitTypes.RenderUnit.RenderPoints:
            return size
        elif units == QgsUnitTypes.RenderUnit.RenderMillimeters:
            return size / 0.352778
        elif units == QgsUnitTypes.RenderUnit.RenderInches:
            return size * 72
        elif units == QgsUnitTypes.RenderUnit.RenderPixels:
            self.push_warning(
                "ArcGIS Pro does not support pixel units. Symbol will be converted to point sizes assuming 96 dpi.",
                level=Context.WARNING,
            )
            return size / 96 * 72  # assume 96 dpi
        elif units == QgsUnitTypes.RenderUnit.RenderMetersInMapUnits:
            return size
        elif units in (
            QgsUnitTypes.RenderUnit.RenderMapUnits,
            QgsUnitTypes.RenderUnit.RenderPercentage,
        ):
            unit_name = QgsUnitTypes.toString(units)
            self.push_warning(
                'ArcGIS Pro does not support "{}" units'.format(unit_name),
                level=Context.WARNING,
            )
            return None

        raise NotImplementedException(
            "Converting units of type {} is not supported".format(units)
        )

    def convert_map_units_to_meters(self, size_map_units: float):
        """
        Converts map units to approximate meters
        """
        if self.approx_map_area:
            if (
                self.approx_map_area.crs().mapUnits()
                == QgsUnitTypes.DistanceUnit.DistanceDegrees
                or not self.approx_map_area.crs().isValid()
            ):
                center = self.approx_map_area.center()

                lon2 = 1
                lat = center.y()
                lat, dlon = map(radians, [lat, lon2])
                # haversine formula
                a = cos(lat) * cos(lat) * sin(dlon / 2) ** 2
                c = 2 * asin(sqrt(a))
                conversion_factor = 6371000 * c
            else:
                conversion_factor = QgsUnitTypes.fromUnitToUnitFactor(
                    self.approx_map_area.crs().mapUnits(),
                    QgsUnitTypes.DistanceUnit.DistanceMeters,
                )
        else:
            conversion_factor = QgsUnitTypes.fromUnitToUnitFactor(
                QgsUnitTypes.DistanceUnit.DistanceDegrees,
                QgsUnitTypes.DistanceUnit.DistanceMeters,
            )

        return size_map_units * conversion_factor

    def fix_line_width(self, size) -> float:
        """
        Applies line width tweaks to better represent original ESRI symbols
        """
        if not self.apply_conversion_tweaks:
            return size

        if size <= 0.4:
            # ESRI renders this closer to a "hairline" width in QGIS land
            return 0
        return size

    def resolve_filename(self, document_file_name: str, file_name: str) -> str:
        """
        Resolves a filename to a resource based on the parent document
        path and any other clues we can use to try to intelligently match
        to an existing path
        """
        document_path = Path(document_file_name)

        original_path = Path(file_name)
        if original_path.exists():
            return file_name

        if self.original_path:
            # if we know the original saved path of a mxd document,
            # see if we can resolve the layer as a path relative
            # to that original path, corrected to the new location
            # of the mxd document
            if self.original_path.suffix.lower() == ".gdb":
                original_project_path_base = self.original_path.parent.as_posix()
            else:
                original_project_path_base = self.original_path.as_posix()
            file_name_base = original_path.as_posix()
            if file_name_base.startswith(original_project_path_base):
                candidate_relative_path = original_path.as_posix()[
                    len(original_project_path_base) + 1 :
                ]
                # look relative to .mxd for matching file
                candidate = document_path.parent / candidate_relative_path
                if candidate.exists():
                    return candidate.as_posix()

        if document_path.suffix.lower() in (
            ".lyr",
            ".lyrx",
        ) or original_path.suffix in (".fdl",):
            input_directory = document_path.parent

            original_path = Path(file_name)

            if not original_path.exists():
                # look next to .lyr for matching file
                candidate = input_directory / original_path.name
                if candidate.exists():
                    return candidate.as_posix()

        return file_name

    @staticmethod
    def find_relative_path(
        path: str, diverge_path: Union[str, Path]
    ) -> Union[bool, str]:
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
            return "."

        try:
            output = os.path.relpath(path, diverge_path)
        except ValueError:
            return False

        if output == ".":
            return "."
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

        if converted_path == "":
            converted_path = "."

        try:
            converted_path = str(WindowsPath(converted_path))
        except NotImplementedError:
            converted_path = converted_path.replace("/", "\\")

        if (
            is_rel_path
            and not converted_path.startswith(".")
            and not converted_path.startswith("..")
        ):
            converted_path = ".\\" + converted_path

        return converted_path
