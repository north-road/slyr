#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class RouteAnomalyProperties(Object):
    """
    RouteAnomalyProperties
    """

    @staticmethod
    def cls_id():
        return '17dac573-752f-483f-bba2-3e7fa4ab34c1'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.minimum_scale = None
        self.maximum_scale = None
        self.show_measures_no_value = False
        self.inconsistent_ignore_digitized_direction = False
        self.inconsistent_ignore_where_consecutive_is_same = False
        self.show_inconsistent_measures = False
        self.filter = None
        self.identify_properties = None
        self.symbol_line_measures_no_val = None
        self.symbol_marker_measures_no_val = None
        self.symbol_line_measures_inconsistent = None
        self.symbol_marker_measures_inconsistent = None

    def read(self, stream: Stream, version):
        self.minimum_scale = stream.read_double('minimum scale')
        self.maximum_scale = stream.read_double('maximum scale')
        self.show_measures_no_value = stream.read_ushort('show where measures do not have value') != 0
        self.inconsistent_ignore_digitized_direction = stream.read_ushort(
            'inconsistent is increase ignore digitized') != 0
        self.inconsistent_ignore_where_consecutive_is_same = stream.read_ushort(
            'inconsistent ignore where consecutive is same') != 0
        self.show_inconsistent_measures = stream.read_ushort('show inconsistent measures') != 0

        self.filter = stream.read_object('filter')
        stream.read_int('count', expected=4)

        self.symbol_line_measures_no_val = stream.read_object('symbol line measures no val')
        self.symbol_marker_measures_no_val = stream.read_object('symbol marker measures no val')
        self.symbol_line_measures_inconsistent = stream.read_object('symbol line measures inconsistent')
        self.symbol_marker_measures_inconsistent = stream.read_object('symbol marker measures inconsistent')

        self.identify_properties = stream.read_object('identify properties')

        stream.read_int('unknown', expected=63)

    #       stream.read_int('unknown', expected=68)
    #       stream.read_int('unknown', expected=0)

    #        if stream.read_int('unknown', expected=(63, 68)) == 63:
    #            stream.read_double('unknown', expected=0.1)
    #            stream.read_double('unknown', expected=99)

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'minimum_scale': self.minimum_scale,
            'maximum_scale': self.maximum_scale,
            'show_measures_no_value': self.show_measures_no_value,
            'inconsistent_ignore_digitized_direction': self.inconsistent_ignore_digitized_direction,
            'inconsistent_ignore_where_consecutive_is_same': self.inconsistent_ignore_where_consecutive_is_same,
            'show_inconsistent_measures': self.show_inconsistent_measures,
            'filter': self.filter.to_dict() if self.filter else None,
            'identify_properties': self.identify_properties.to_dict() if self.identify_properties else None,
            'symbol_line_measures_no_val': self.symbol_line_measures_no_val.to_dict() if self.symbol_line_measures_no_val else None,
            'symbol_marker_measures_no_val': self.symbol_marker_measures_no_val.to_dict() if self.symbol_marker_measures_no_val else None,
            'symbol_line_measures_inconsistent': self.symbol_line_measures_inconsistent.to_dict() if self.symbol_line_measures_inconsistent else None,
            'symbol_marker_measures_inconsistent': self.symbol_marker_measures_inconsistent.to_dict() if self.symbol_marker_measures_inconsistent else None,
        }
