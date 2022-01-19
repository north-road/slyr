#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream
from .units import Units


class MaplexLabelEngineLayerProperties(Object):
    """
    MaplexLabelEngineLayerProperties
    """

    @staticmethod
    def cls_id():
        return '20664808-0d1c-11d2-a26f-080009b6f22b'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.label_features = True
        self.class_name = ''
        self.class_filter = ''
        self.expression = None
        self.advanced_expression = False
        self.text_symbol = None
        self.scale_range_min = 0
        self.scale_range_max = 0
        self.overposter = None
        self.expression_parser = None
        self.offset = 0
        self.label_which_features = 0
        self.symbol_id = 0
        self.layer_full_extent = None
        self.scale_ratio = 0
        self.reference_scale = 0
        self.units_world_coordinates = Units.DISTANCE_FEET
        self.priority = 0
        self.create_unplaced_elements = False
        self.feature_linked = False
        self.use_output = False
        self.annotation_class_id = 0
        self.add_unplaced_to_graphics_container = True

    @staticmethod
    def compatible_versions():
        return [11]

    def read(self, stream: Stream, version):
        self.expression = stream.read_string('expression')
        self.advanced_expression = stream.read_ushort('advanced expression') == 0
        self.offset = stream.read_double('offset')
        self.label_which_features = stream.read_int('label which features')  # esriLabelWhichFeatures
        self.create_unplaced_elements = stream.read_ushort('create unplaced elements') != 0
        self.feature_linked = stream.read_ushort('feature linked') != 0
        self.use_output = stream.read_ushort('use output')
        self.symbol_id = stream.read_ushort('symbol id')

        self.add_unplaced_to_graphics_container = stream.read_ushort('add unplaced to graphics container') != 0

        self.scale_range_max = stream.read_double('scale range max')
        self.scale_range_min = stream.read_double('scale range min')

        self.label_features = stream.read_ushort('label features?') != 0
        self.class_name = stream.read_string('label class name')
        self.class_filter = stream.read_string('class filter')

        self.text_symbol = stream.read_object('text symbol')

        self.expression_parser = stream.read_object('expression parser')

        self.layer_full_extent = stream.read_object('layer full extent')
        self.scale_ratio = stream.read_double('scale ratio')
        self.reference_scale = stream.read_double('reference scale')
        self.units_world_coordinates = stream.read_int('units of world coordinates')

        self.priority = stream.read_int('priority')
        stream.read_int('unknown', expected=0)
        stream.read_int('unknown', expected=0)
        stream.read_int('unknown', expected=0)
        stream.read_int('unknown', expected=0)
        stream.read_ushort('annotations related annotations=65535')

        self.overposter = stream.read_object('overposter')

        self.annotation_class_id = stream.read_int('annotation class id')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'label_features': self.label_features,
            'class_name': self.class_name,
            'class_filter': self.class_filter,
            'expression': self.expression,
            'scale_range_min': self.scale_range_min,
            'scale_range_max': self.scale_range_max,
            'text_symbol': self.text_symbol.to_dict() if self.text_symbol else None,
            'overposter': self.overposter.to_dict() if self.overposter else None,
            'expression_parser': self.expression_parser.to_dict() if self.expression_parser else None,
            'offset': self.offset,
            'label_which_features': self.label_which_features,
            'symbol_id': self.symbol_id,
            'layer_full_extent': self.layer_full_extent.to_dict() if self.layer_full_extent else None,
            'scale_ratio': self.scale_ratio,
            'reference_scale': self.reference_scale,
            'units_world_coordinates': Units.distance_unit_to_string(self.units_world_coordinates),
            'priority': self.priority,
            'create_unplaced_elements': self.create_unplaced_elements,
            'feature_linked': self.feature_linked,
            'use_output': self.use_output,
            'annotation_class_id': self.annotation_class_id,
            'add_unplaced_to_graphics_container': self.add_unplaced_to_graphics_container,
        }
