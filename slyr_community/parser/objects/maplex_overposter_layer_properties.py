#!/usr/bin/env python
"""
Serializable object subclass

"""

from ..object import Object
from .maplex_utils import MaplexUtils
from ..stream import Stream


class MaplexOverposterLayerProperties(Object):
    """
    MaplexOverposterLayerProperties
    """

    POINT_PLACEMENT_BEST = 0
    POINT_PLACEMENT_CENTERED = 1
    POINT_PLACEMENT_NORTH = 2
    POINT_PLACEMENT_NORTHEAST = 3
    POINT_PLACEMENT_EAST = 4
    POINT_PLACEMENT_SOUTHEAST = 5
    POINT_PLACEMENT_SOUTH = 6
    POINT_PLACEMENT_SOUTHWEST = 7
    POINT_PLACEMENT_WEST = 8
    POINT_PLACEMENT_NORTHWEST = 9

    LINE_PLACEMENT_CENTERED_HORIZONTAL_ON_LINE = 0
    LINE_PLACEMENT_CENTERED_STRAIGHT_ON_LINE = 1
    LINE_PLACEMENT_CENTERED_CURVED_ON_LINE = 2
    LINE_PLACEMENT_CENTERED_PERPENDICULAR_ON_LINE = 3
    LINE_PLACEMENT_OFFSET_HORIZONTAL_FROM_LINE = 4
    LINE_PLACEMENT_OFFSET_STRAIGHT_FROM_LINE = 5
    LINE_PLACEMENT_OFFSET_CURVED_FROM_LINE = 6
    LINE_PLACEMENT_OFFSET_PERPENDICULAR_FROM_LINE = 7

    POLYGON_PLACEMENT_HORIZONTAL_IN_POLYGON = 0
    POLYGON_PLACEMENT_STRAIGHT_IN_POLYGON = 1
    POLYGON_PLACEMENT_CURVED_IN_POLYGON = 2
    POLYGON_PLACEMENT_HORIZONTAL_AROUND_POLYGON = 3
    POLYGON_PLACEMENT_REPEAT_ON_BOUNDARY = 4
    POLYGON_PLACEMENT_CURVED_AROUND_POLYGON = 5

    CONSTRAIN_OFFSET_NONE = 0
    CONSTRAIN_OFFSET_ABOVE_LINE = 1
    CONSTRAIN_OFFSET_BELOW_LINE = 2
    CONSTRAIN_OFFSET_LEFT_OF_LINE = 3
    CONSTRAIN_OFFSET_RIGHT_OF_LINE = 4

    @staticmethod
    def cls_id():
        return '20664808-41c9-11d1-880a-080009ec732a'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.is_barrier = False
        self.place_labels = False
        self.place_symbols = False
        self.properties = None
        self.point_placement_method = MaplexOverposterLayerProperties.POINT_PLACEMENT_BEST
        self.user_defined_zones = False
        self.point_placement_priorities = None
        self.may_shift_label_on_fixed_position = False
        self.offset_along_line_properties = None
        self.offset_constraint = MaplexOverposterLayerProperties.CONSTRAIN_OFFSET_NONE
        self.rotation_properties = None
        self.stacking_properties = None
        self.feature_weight = 100
        self.is_background_label = False
        self.label_margin_buffer_percent = 15
        self.max_offset = 100
        self.offset = 0
        self.offset_unit = MaplexUtils.UNIT_POINT
        self.place_overlapping = False
        self.align_to_graticule = False
        self.reduce_duplicates = False
        self.reduce_duplicates_distance = 0
        self.line_placement_method = MaplexOverposterLayerProperties.LINE_PLACEMENT_CENTERED_CURVED_ON_LINE
        self.spread_characters_max = 0
        self.spread_words_max = 0
        self.repeat_labels = False
        self.repeat_distance = 0
        self.min_feature_size = 0
        self.preferred_end_of_line_clearance = 0
        self.min_end_of_line_clearance = 0
        self.spread_words = False
        self.spread_chars = False
        self.polygon_placement_method = MaplexOverposterLayerProperties.POLYGON_PLACEMENT_CURVED_IN_POLYGON
        self.place_outside_polygon = True
        self.polygon_boundary_weight = 0
        self.overrun = False
        self.can_overrun_feature = False
        self.overrun_allow_asymmetric = False
        self.may_place_primary_label_under_when_stacked = False
        self.polygon_land_parcel_placement = False
        self.max_overrun = 0
        self.abbreviation_enabled = False
        self.reduce_font_size = False
        self.font_size_lower_limit_points = 0
        self.font_size_step_interval_points = 0
        self.font_width_compression_limit_percent = 0
        self.font_width_compression_step_interval = 0
        self.tag_unplaced = False
        self.can_remove_overlapping = False
        self.can_truncate = False
        self.align_to_direction_of_line = False
        self.try_horizontal_first = False
        self.dictionary_name = ''
        self.feature_buffer = 0
        self.feature_type = 0  # esriBasicOverposterFeatureType
        self.priority = 0

    @staticmethod
    def compatible_versions():
        return [22]

    @staticmethod
    def point_placement_to_string(placement):
        if placement == MaplexOverposterLayerProperties.POINT_PLACEMENT_BEST:
            return 'best'
        elif placement == MaplexOverposterLayerProperties.POINT_PLACEMENT_CENTERED:
            return 'centered'
        elif placement == MaplexOverposterLayerProperties.POINT_PLACEMENT_NORTH:
            return 'north'
        elif placement == MaplexOverposterLayerProperties.POINT_PLACEMENT_NORTHEAST:
            return 'northeast'
        elif placement == MaplexOverposterLayerProperties.POINT_PLACEMENT_EAST:
            return 'east'
        elif placement == MaplexOverposterLayerProperties.POINT_PLACEMENT_SOUTHEAST:
            return 'southeast'
        elif placement == MaplexOverposterLayerProperties.POINT_PLACEMENT_SOUTH:
            return 'south'
        elif placement == MaplexOverposterLayerProperties.POINT_PLACEMENT_SOUTHWEST:
            return 'southwest'
        elif placement == MaplexOverposterLayerProperties.POINT_PLACEMENT_WEST:
            return 'west'
        elif placement == MaplexOverposterLayerProperties.POINT_PLACEMENT_NORTHWEST:
            return 'northwest'

        return None

    @staticmethod
    def line_placement_to_string(placement):
        if placement == MaplexOverposterLayerProperties.LINE_PLACEMENT_CENTERED_HORIZONTAL_ON_LINE:
            return 'centered_horizontal_on_line'
        elif placement == MaplexOverposterLayerProperties.LINE_PLACEMENT_CENTERED_STRAIGHT_ON_LINE:
            return 'centered_straight_on_line'
        elif placement == MaplexOverposterLayerProperties.LINE_PLACEMENT_CENTERED_CURVED_ON_LINE:
            return 'centered_curved_on_line'
        elif placement == MaplexOverposterLayerProperties.LINE_PLACEMENT_CENTERED_PERPENDICULAR_ON_LINE:
            return 'centered_perpendicular_on_line'
        elif placement == MaplexOverposterLayerProperties.LINE_PLACEMENT_OFFSET_HORIZONTAL_FROM_LINE:
            return 'offset_horizontal_from_line'
        elif placement == MaplexOverposterLayerProperties.LINE_PLACEMENT_OFFSET_STRAIGHT_FROM_LINE:
            return 'offset_straight_from_line'
        elif placement == MaplexOverposterLayerProperties.LINE_PLACEMENT_OFFSET_CURVED_FROM_LINE:
            return 'offset_curved_from_line'
        elif placement == MaplexOverposterLayerProperties.LINE_PLACEMENT_OFFSET_PERPENDICULAR_FROM_LINE:
            return 'offset_perpendicular_from_line'
        return None

    @staticmethod
    def offset_constraint_to_string(constraint):
        if constraint == MaplexOverposterLayerProperties.CONSTRAIN_OFFSET_NONE:
            return 'none'
        elif constraint == MaplexOverposterLayerProperties.CONSTRAIN_OFFSET_ABOVE_LINE:
            return 'above_line'
        elif constraint == MaplexOverposterLayerProperties.CONSTRAIN_OFFSET_BELOW_LINE:
            return 'below_line'
        elif constraint == MaplexOverposterLayerProperties.CONSTRAIN_OFFSET_LEFT_OF_LINE:
            return 'left_of_line'
        elif constraint == MaplexOverposterLayerProperties.CONSTRAIN_OFFSET_RIGHT_OF_LINE:
            return 'right_of_line'
        return None

    @staticmethod
    def polygon_placement_method_to_string(method):
        if method == MaplexOverposterLayerProperties.POLYGON_PLACEMENT_HORIZONTAL_IN_POLYGON:
            return 'horizontal_in_polygon'
        elif method == MaplexOverposterLayerProperties.POLYGON_PLACEMENT_STRAIGHT_IN_POLYGON:
            return 'straight_in_polygon'
        elif method == MaplexOverposterLayerProperties.POLYGON_PLACEMENT_CURVED_IN_POLYGON:
            return 'curved_in_polygon'
        elif method == MaplexOverposterLayerProperties.POLYGON_PLACEMENT_HORIZONTAL_AROUND_POLYGON:
            return 'horizontal_around_polygon'
        elif method == MaplexOverposterLayerProperties.POLYGON_PLACEMENT_REPEAT_ON_BOUNDARY:
            return 'repeat_on_boundary'
        elif method == MaplexOverposterLayerProperties.POLYGON_PLACEMENT_CURVED_AROUND_POLYGON:
            return 'curved_around_polygon'
        return None

    def read(self, stream: Stream, version):
        self.place_labels = stream.read_ushort('place labels') != 0
        self.place_symbols = stream.read_ushort('place symbols') != 0
        self.is_barrier = stream.read_ushort('is barrier') != 0
        self.feature_type = stream.read_int('feature type')

        self.point_placement_method = stream.read_int('point placement')
        self.line_placement_method = stream.read_int('line placement')
        self.polygon_placement_method = stream.read_int('polygon placement')
        self.place_outside_polygon = stream.read_ushort('place outside polygon') != 0

        self.polygon_land_parcel_placement = stream.read_ushort('land parcel placement') != 0
        self.offset = stream.read_double('offset from point')
        self.offset_unit = stream.read_int('offset from point unit')
        self.max_offset = stream.read_double('point max offset')
        self.offset_constraint = stream.read_int('offset constraint')
        self.point_placement_priorities = stream.read_object('user defined zone priorities')
        self.may_shift_label_on_fixed_position = stream.read_ushort('may shift label on fixed position') != 0
        self.may_place_primary_label_under_when_stacked = stream.read_ushort(
            'may place primary label under when stacked') != 0

        self.repeat_labels = stream.read_ushort('repeat labels') != 0
        self.repeat_distance = stream.read_double('repeat distance')

        self.spread_chars = stream.read_ushort('spread chars') != 0
        self.spread_words_max = stream.read_double('spread words max')
        self.preferred_end_of_line_clearance = stream.read_double('preferred end of line clearance')
        self.min_end_of_line_clearance = stream.read_double('min end of line clearance')

        self.overrun = stream.read_ushort('overrun') == 0
        self.stacking_properties = stream.read_object('stacking properties')

        self.can_overrun_feature = stream.read_ushort('can overrun feature') != 0
        self.max_overrun = stream.read_double('max overrun')
        self.abbreviation_enabled = stream.read_ushort('abbreviate') != 0
        self.can_truncate = stream.read_ushort('can truncate') != 0
        self.reduce_font_size = stream.read_ushort('reduce font size') != 0
        self.font_size_lower_limit_points = stream.read_double('font size lower limit points')
        self.font_size_step_interval_points = stream.read_double('font size step interval points')
        self.font_width_compression_limit_percent = stream.read_double('font width compression limit %')
        self.font_width_compression_step_interval = stream.read_double('font width compression step interval')

        self.place_overlapping = stream.read_ushort('place overlapping') != 0

        stream.read_ushort('unknown', expected=0)
        stream.read_ushort('unknown', expected=0)
        self.feature_weight = stream.read_int('feature weight')
        self.polygon_boundary_weight = stream.read_int('polygon boundary weight')
        self.can_remove_overlapping = stream.read_ushort('can remove overlapping') != 0

        self.reduce_duplicates = stream.read_ushort('reduce duplicates') != 0
        self.reduce_duplicates_distance = stream.read_double('reduce duplicates by')

        self.user_defined_zones = stream.read_ushort('user defined zones') != 0

        self.spread_words = stream.read_ushort('spread words') != 0
        self.spread_characters_max = stream.read_double('spread characters max')

        self.align_to_graticule = stream.read_ushort('align to graticule') != 0

        self.offset_along_line_properties = stream.read_object('offset along line properties')

        stream.read_int('unknown', expected=1)

        self.rotation_properties = stream.read_object('rotation properties')

        self.priority = stream.read_int('priority')

        self.dictionary_name = stream.read_string('dictionary name')
        self.align_to_direction_of_line = stream.read_ushort('align to direction of line') != 0
        self.try_horizontal_first = stream.read_ushort('try horizontal first') != 0

        self.is_background_label = stream.read_ushort('is background label') != 0
        self.tag_unplaced = stream.read_ushort('tag unplaced') != 0
        self.overrun_allow_asymmetric = stream.read_ushort('overrun allow asymmetric') != 0
        self.min_feature_size = stream.read_double('min feature size')

        self.label_margin_buffer_percent = stream.read_int('label margin buffer %')
        self.feature_buffer = stream.read_int('feature buffer')
        self.properties = stream.read_object('properties dict')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'place_labels': self.place_labels,
            'is_barrier': self.is_barrier,
            'place_symbols': self.place_symbols,
            'tag_unplaced': self.tag_unplaced,
            'point_placement': MaplexOverposterLayerProperties.point_placement_to_string(self.point_placement_method),
            'point_placement_priorities': self.point_placement_priorities.to_dict() if self.point_placement_priorities else None,
            'user_defined_zones': self.user_defined_zones,
            'may_shift_label_on_fixed_position': self.may_shift_label_on_fixed_position,
            'offset_along_line_properties': self.offset_along_line_properties.to_dict() if self.offset_along_line_properties else None,
            'rotation_properties': self.rotation_properties.to_dict() if self.rotation_properties else None,
            'stacking_properties': self.stacking_properties.to_dict() if self.stacking_properties else None,
            'properties': self.properties.to_dict() if self.properties else None,
            'feature_weight': self.feature_weight,
            'is_background_label': self.is_background_label,
            'margin_buffer_percent': self.label_margin_buffer_percent,
            'max_offset': self.max_offset,
            'offset': self.offset,
            'offset_unit': MaplexUtils.unit_to_string(self.offset_unit),
            'place_overlapping': self.place_overlapping,
            'align_to_graticule': self.align_to_graticule,
            'reduce_duplicates': self.reduce_duplicates,
            'reduce_duplicates_distance': self.reduce_duplicates_distance,
            'line_placement': MaplexOverposterLayerProperties.line_placement_to_string(self.line_placement_method),
            'spread_characters_max': self.spread_characters_max,
            'spread_words_max': self.spread_words_max,
            'repeat_labels': self.repeat_labels,
            'repeat_distance': self.repeat_distance,
            'min_feature_size': self.min_feature_size,
            'offset_constraint': MaplexOverposterLayerProperties.offset_constraint_to_string(self.offset_constraint),
            'preferred_end_of_line_clearance': self.preferred_end_of_line_clearance,
            'min_end_of_line_clearance': self.min_end_of_line_clearance,
            'spread_words': self.spread_words,
            'polygon_placement': MaplexOverposterLayerProperties.polygon_placement_method_to_string(
                self.polygon_placement_method),
            'place_outside_polygon': self.place_outside_polygon,
            'polygon_boundary_weight': self.polygon_boundary_weight,
            'overrun_allow_asymmetric': self.overrun_allow_asymmetric,
            'may_place_primary_label_under_when_stacked': self.may_place_primary_label_under_when_stacked,
            'spread_chars': self.spread_chars,
            'overrun': self.overrun,
            'can_overrun_feature': self.can_overrun_feature,
            'polygon_land_parcel_placement': self.polygon_land_parcel_placement,
            'reduce_font_size': self.reduce_font_size,
            'font_size_lower_limit_points': self.font_size_lower_limit_points,
            'font_size_step_interval_points': self.font_size_step_interval_points,
            'font_width_compression_limit_percent': self.font_width_compression_limit_percent,
            'font_width_compression_step_interval': self.font_width_compression_step_interval,
            'abbreviate': self.abbreviation_enabled,
            'max_overrun': self.max_overrun,
            'can_remove_overlapping': self.can_remove_overlapping,
            'can_truncate': self.can_truncate,
            'align_to_direction_of_line': self.align_to_direction_of_line,
            'try_horizontal_first': self.try_horizontal_first,
            'dictionary_name': self.dictionary_name,
            'feature_buffer': self.feature_buffer,
            'feature_type': self.feature_type,
            'priority': self.priority
        }
