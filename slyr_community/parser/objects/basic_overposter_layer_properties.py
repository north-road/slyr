#!/usr/bin/env python
"""
Serializable object subclass

COMPLETE INTERPRETATION
"""

from ..object import Object
from ..stream import Stream


class BasicOverposterLayerProperties(Object):
    """
    BasicOverposterLayerProperties
    """

    POINT_PLACEMENT_AROUND = 0
    POINT_PLACEMENT_ON_TOP = 1
    POINT_PLACEMENT_ROTATION_FIELD = 3
    POINT_PLACEMENT_SPECIFIED_ANGLES = 2

    POLYGON_PLACEMENT_ALWAYS_HORIZONTAL = 0
    POLYGON_PLACEMENT_ALWAYS_STRAIGHT = 1
    POLYGON_PLACEMENT_MIXED = 2

    NUM_NO_RESTRICTION = 0
    NUM_ONE_PER_NAME = 1
    NUM_ONE_PER_FEATURE = 2
    NUM_ONE_PER_PART = 3

    WEIGHT_NONE = 0
    WEIGHT_LOW = 1
    WEIGHT_MED = 2
    WEIGHT_HIGH = 3

    OVERPOSTER_POINT = 0
    OVERPOSTER_LINE = 1
    OVERPOSTER_POLYGON = 2

    ROTATION_GEOGRAPHIC = 0
    ROTATION_ARITHMETIC = 1
    ROTATION_RADIANS = 2
    ROTATION_AV3 = 3

    @staticmethod
    def cls_id():
        return 'ee535289-41c9-11d1-880a-080009ec732a'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.is_barrier = False
        self.point_placement_method = BasicOverposterLayerProperties.POINT_PLACEMENT_AROUND
        self.point_placement_priorities = None
        self.point_label_angle_field = None
        self.point_label_angle_perpendicular = False
        self.point_place_over_feature = False
        self.specified_point_angles = []
        self.polygon_placement_method = BasicOverposterLayerProperties.POLYGON_PLACEMENT_ALWAYS_HORIZONTAL
        self.polygon_only_inside = False
        self.line_label_position = None
        self.line_label_priorities = None
        self.label_margin = 0.0
        self.offset = 0.0
        self.number_restriction = BasicOverposterLayerProperties.NUM_NO_RESTRICTION
        self.feature_weight = BasicOverposterLayerProperties.WEIGHT_NONE
        self.label_weight = BasicOverposterLayerProperties.WEIGHT_NONE
        self.place_overlapping = False
        self.geometry_type = BasicOverposterLayerProperties.OVERPOSTER_POINT
        self.generate_unplaced = True
        self.max_distance_from_feature = 0
        self.point_label_angle_type = BasicOverposterLayerProperties.ROTATION_GEOGRAPHIC
        self.place_labels = True
        self.place_symbols = True

    @staticmethod
    def compatible_versions():
        return [2, 3, 4, 6]

    @staticmethod
    def point_placement_to_string(placement):
        """
        Converts a point placement enum to a string
        """
        if placement == BasicOverposterLayerProperties.POINT_PLACEMENT_AROUND:
            return 'around'
        elif placement == BasicOverposterLayerProperties.POINT_PLACEMENT_ON_TOP:
            return 'on_top'
        elif placement == BasicOverposterLayerProperties.POINT_PLACEMENT_ROTATION_FIELD:
            return 'rotation_from_field'
        elif placement == BasicOverposterLayerProperties.POINT_PLACEMENT_SPECIFIED_ANGLES:
            return 'specified_angles'
        return None

    @staticmethod
    def polygon_placement_to_string(placement):
        """
        Converts a polygon placement enum to a string
        """
        if placement == BasicOverposterLayerProperties.POLYGON_PLACEMENT_ALWAYS_STRAIGHT:
            return 'always_straight'
        elif placement == BasicOverposterLayerProperties.POLYGON_PLACEMENT_ALWAYS_HORIZONTAL:
            return 'always_horizontal'
        elif placement == BasicOverposterLayerProperties.POLYGON_PLACEMENT_MIXED:
            return 'mixed'
        return None

    @staticmethod
    def num_restriction_to_string(restriction):
        """
        Converts label number restriction to a string
        """
        if restriction == BasicOverposterLayerProperties.NUM_NO_RESTRICTION:
            return 'none'
        elif restriction == BasicOverposterLayerProperties.NUM_ONE_PER_NAME:
            return 'one_per_name'
        elif restriction == BasicOverposterLayerProperties.NUM_ONE_PER_FEATURE:
            return 'one_per_feature'
        elif restriction == BasicOverposterLayerProperties.NUM_ONE_PER_PART:
            return 'one_per_part'
        return None

    @staticmethod
    def weight_to_string(weight):
        """
        Converts weight enum to a string
        """
        if weight == BasicOverposterLayerProperties.WEIGHT_NONE:
            return 'none'
        elif weight == BasicOverposterLayerProperties.WEIGHT_LOW:
            return 'low'
        elif weight == BasicOverposterLayerProperties.WEIGHT_MED:
            return 'medium'
        elif weight == BasicOverposterLayerProperties.WEIGHT_HIGH:
            return 'high'
        return None

    def read(self, stream: Stream, version):
        # these seem ignored?
        self.place_labels = stream.read_ushort('place labels') != 0
        self.place_symbols = stream.read_ushort('place symbols') != 0
        self.is_barrier = stream.read_ushort('is barrier') != 0

        self.feature_weight = stream.read_int('feature weight')
        self.label_weight = stream.read_int('label weight')
        self.number_restriction = stream.read_int('number restriction')

        self.line_label_position = stream.read_object('line label position')
        self.line_label_priorities = stream.read_object('line label placement priorities')
        self.generate_unplaced = stream.read_ushort('generate unplaced') != 0

        self.point_placement_method = stream.read_int('point placement method')
        self.label_margin = stream.read_double('label margin size')
        self.point_place_over_feature = stream.read_ushort('place point labels on top of features') != 0
        self.point_placement_priorities = stream.read_object('point placement priorities')
        number_angles = stream.read_int('number of angle places')
        for i in range(number_angles):
            self.specified_point_angles.append(stream.read_double('angle {}'.format(i + 1)))
        # point placement field??

        self.offset = stream.read_double('offset')
        self.geometry_type = stream.read_int('geometry type', expected=(0, 1, 2))

        if version < 3:
            return

        self.max_distance_from_feature = stream.read_double('max distance')
        if version < 4:
            return

        self.point_label_angle_type = stream.read_int('point label angle type')
        self.point_label_angle_field = stream.read_string('point label angle by field')
        self.point_label_angle_perpendicular = stream.read_ushort('point label angle perpendicular') != 0

        if version > 4:
            self.polygon_placement_method = stream.read_int('polygon placement')
            self.polygon_only_inside = stream.read_ushort('polygon only inside') != 0
            self.place_overlapping = stream.read_ushort('overlapping') == 0

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'line_label_position': self.line_label_position.to_dict() if self.line_label_position else None,
            'line_label_priorities': self.line_label_priorities.to_dict() if self.line_label_priorities else None,
            'point_placement_method': BasicOverposterLayerProperties.point_placement_to_string(
                self.point_placement_method),
            'point_placement_priorities': self.point_placement_priorities.to_dict() if self.point_placement_priorities else None,
            'point_label_angle_field': self.point_label_angle_field,
            'point_label_angle_perpendicular': self.point_label_angle_perpendicular,
            'point_place_over_feature': self.point_place_over_feature,
            'specified_point_angles': self.specified_point_angles,
            'polygon_placement_method': BasicOverposterLayerProperties.polygon_placement_to_string(
                self.polygon_placement_method),
            'polygon_only_inside': self.polygon_only_inside,
            'margin_size': self.label_margin,
            'offset': self.offset,
            'number_restriction': BasicOverposterLayerProperties.num_restriction_to_string(self.number_restriction),
            'feature_weight': BasicOverposterLayerProperties.weight_to_string(self.feature_weight),
            'label_weight': BasicOverposterLayerProperties.weight_to_string(self.label_weight),
            'place_overlapping': self.place_overlapping,
            'geometry_type': self.geometry_type,
            'generate_unplaced': self.generate_unplaced,
            'max_distance_from_feature': self.max_distance_from_feature,
            'point_label_angle_type': self.point_label_angle_type,
            'is_barrier': self.is_barrier,
            'place_labels': self.place_labels,
            'place_symbols': self.place_symbols
        }
