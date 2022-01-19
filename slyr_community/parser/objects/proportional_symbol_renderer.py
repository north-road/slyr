#!/usr/bin/env python
"""
Serializable object subclass
"""

from .vector_renderer import VectorRendererBase
from .units import Units
from ..stream import Stream


class ProportionalSymbolRenderer(VectorRendererBase):
    """
    ProportionalSymbolRenderer
    """

    MARKER_CIRCLE = 0
    MARKER_SQUARE = 1

    BY_RANGE = 0
    BY_RADIUS = 1
    BY_AREA = 2

    @staticmethod
    def cls_id():
        return '4eab568e-8f9c-11d2-ab21-00c04fa334b3'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.attribute = ''
        self.symbol = None
        self.legend_group = None
        self.exclusion_filter = ''
        self.compensate_using_flannery = False
        self.proportional_symbol_units = Units.DISTANCE_UNKNOWN
        self.normalize_by_attribute = ''
        self.normalization_method = VectorRendererBase.NORMALIZE_BY_FIELD
        self.number_legend_classes = 0
        self.marker_style = ProportionalSymbolRenderer.MARKER_SQUARE
        self.scaling_type = ProportionalSymbolRenderer.BY_RANGE
        self.line_width = 0
        self.value_min = 0
        self.value_max = 0
        self.background_symbol = None

    @staticmethod
    def compatible_versions():
        return [5]

    @staticmethod
    def marker_style_to_string(style):
        """
        Converts marker style to string
        """
        if style == ProportionalSymbolRenderer.MARKER_CIRCLE:
            return 'circle'
        elif style == ProportionalSymbolRenderer.MARKER_SQUARE:
            return 'square'
        return None

    @staticmethod
    def scaling_type_to_string(scaling_type):
        """
        Converts scaling type to string
        """
        if scaling_type == ProportionalSymbolRenderer.BY_RANGE:
            return 'by_range'
        elif scaling_type == ProportionalSymbolRenderer.BY_AREA:
            return 'by_area'
        elif scaling_type == ProportionalSymbolRenderer.BY_RADIUS:
            return 'by_radius'
        return None

    def read(self, stream: Stream, version):
        self.attribute = stream.read_string('attribute')
        self.symbol = stream.read_object('symbol')

        self.proportional_symbol_units = stream.read_ushort('proportional units')
        stream.read_ushort('unknown', expected=0)
        self.value_min = stream.read_double('value min')
        self.value_max = stream.read_double('value max')

        self.scaling_type = stream.read_int('scaling type')
        self.number_legend_classes = stream.read_int('legend classes')
        self.compensate_using_flannery = stream.read_ushort('compensate flannery') != 0

        self.marker_style = stream.read_ushort('symbol type')

        stream.read_ushort('unknown', expected=0)

        self.legend_group = stream.read_object('legend group')

        stream.read_int('unknown', expected=0)
        stream.read_int('unknown', expected=0)
        stream.read_int('unknown', expected=0)
        stream.read_int('unknown', expected=0)
        self.normalize_by_attribute = stream.read_string('normalization attribute')
        stream.read_ushort('unknown', expected=0)
        stream.read_ushort('unknown', expected=1)

        self.rotation_attribute = stream.read_string('rotation attribute')
        self.rotation_type = stream.read_int('rotation type ')

        self.background_symbol = stream.read_object('fill symbol')

        self.line_width = stream.read_double('line width')
        self.normalization_method = stream.read_int('normalization method')
        stream.read_int('unknown', expected=3)
        stream.read_ushort('unknown', expected=1)
        stream.read_object('unknown legend group')

        self.exclusion_filter = stream.read_string('exclusion filter')
        stream.read_ushort('unknown', expected=0)

        self.read_irotation_renderer2_properties(stream)

    def to_dict(self):  # pylint: disable=method-hidden
        res = super().to_dict()
        res['attribute'] = self.attribute
        res['symbol'] = self.symbol.to_dict() if self.symbol else None
        res['legend_group'] = self.legend_group.to_dict() if self.legend_group else None
        res['exclusion_filter'] = self.exclusion_filter
        res['compensate_using_flannery'] = self.compensate_using_flannery
        res['proportional_symbol_units'] = Units.distance_unit_to_string(self.proportional_symbol_units)
        res['normalize_by_attribute'] = self.normalize_by_attribute
        res['normalization_method'] = VectorRendererBase.normalize_method_to_string(self.normalization_method)
        res['number_legend_classes'] = self.number_legend_classes
        res['marker_style'] = ProportionalSymbolRenderer.marker_style_to_string(self.marker_style)
        res['scaling_type'] = ProportionalSymbolRenderer.scaling_type_to_string(self.scaling_type)
        res['value_min'] = self.value_min
        res['value_max'] = self.value_max
        res['line_width'] = self.line_width
        res['background_symbol'] = self.background_symbol.to_dict() if self.background_symbol else None

        return res
