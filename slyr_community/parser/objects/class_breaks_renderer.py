#!/usr/bin/env python
"""
Serializable object subclass

NEAR COMPLETE INTERPRETATION - all useful components

"""

from .vector_renderer import VectorRendererBase
from ..stream import Stream
from .classification_utils import ClassificationUtils


class ClassBreaksRenderer(VectorRendererBase):
    """
    ClassBreaksRenderer
    """

    @staticmethod
    def cls_id():
        return 'ae5f7ea2-8b48-11d0-8356-080009b996cc'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.attribute = ''
        self.ramp_name = ''
        self.legend_group = None
        self.show_using_values = False
        self.color_ramp = None
        self.ranges = []
        self.classifier = None
        self.normalization_method = VectorRendererBase.NORMALIZE_BY_FIELD
        self.normalize_by_attribute = ''
        self.st_dev_interval = 0.0
        self.sampling_size = 10000
        self.exclusion_filter = ''
        self.excluded_legend_group = None
        self.show_excluded_class = False
        self.is_graduated_symbol = False
        self.barrier_weight = 0
        self.sort_ascending = False
        self.sampling_method = 0
        self.background_symbol = None
        self.normalization_total = 0
        self.flip_symbols = False

    @staticmethod
    def compatible_versions():
        return [5, 6, 8, 10]

    def read(self, stream: Stream, version):
        self.attribute = stream.read_string('attribute')
        self.ramp_name = stream.read_string('ramp name')
        class_count = stream.read_int('class count')

        maxes = []
        mins = []
        for i in range(class_count):
            maxes.append(stream.read_double('max {}'.format(i + 1)))
        for i in range(class_count):
            mins.append(stream.read_double('min {}'.format(i + 1)))
        for i in range(len(maxes)):
            self.ranges.append([mins[i], maxes[i]])

        stream.read_double('overall min')
        self.legend_group = stream.read_object('legend group')

        stream.read_int('unknown', expected=0)
        stream.read_int('unknown', expected=0)
        stream.read_int('unknown', expected=0)
        stream.read_int('unknown', expected=0)
        res = stream.read_uchar('unknown')  # in (0, 1)
        if res:
            c = stream.read_raw_clsid('classifier')
            assert c in ClassificationUtils.CLSID_TO_CLASSIFIER, c
            self.classifier = ClassificationUtils.CLSID_TO_CLASSIFIER[c]
        self.show_using_values = stream.read_ushort('show using values') == 1
        stream.read_object('format')

        self.normalize_by_attribute = stream.read_string('normalize by attribute')
        self.sort_ascending = stream.read_ushort('sort ascending') != 0
        self.is_graduated_symbol = stream.read_ushort('graduated symbol') != 0
        self.sampling_size = stream.read_int('sampling size')
        self.sampling_method = stream.read_int('sampling method')
        stream.read_ushort('unknown', expected=1)

        self.rotation_attribute = stream.read_string('rotation attribute')
        self.rotation_type = stream.read_int('rotation type ')

        self.st_dev_interval = stream.read_double('st dev interval')

        self.background_symbol = stream.read_object('background symbol')

        self.normalization_method = stream.read_int('normalization method')
        self.normalization_total = stream.read_double('normalization total')
        self.barrier_weight = stream.read_int('barrier weight')
        stream.read_ushort('unknown', expected=1)

        self.excluded_legend_group = stream.read_object('excluded legend group')

        self.exclusion_filter = stream.read_string('exclusion filter')
        self.show_excluded_class = stream.read_ushort('show excluded class') != 0

        if version > 5:
            self.read_irotation_renderer2_properties(stream)
            self.read_graduated_size_properties(stream)

        if version > 6:
            self.color_ramp = stream.read_object('color ramp')

            stream.read_int('unknown', expected=0)
            stream.read_int('unknown', expected=0)
            stream.read_int('unknown', expected=0)
            stream.read_int('unknown', expected=0)
            self.flip_symbols = stream.read_ushort('flip symbols') != 0

    def to_dict(self):  # pylint: disable=method-hidden
        res = super().to_dict()
        res['attribute'] = self.attribute
        res['ramp_name'] = self.ramp_name
        res['legend_group'] = self.legend_group.to_dict() if self.legend_group else None
        res['show_using_values'] = self.show_using_values
        res['color_ramp'] = self.color_ramp.to_dict() if self.color_ramp else None
        res['ranges'] = self.ranges
        res['classifier'] = ClassificationUtils.classifier_to_string(self.classifier)
        res['normalize_by_attribute'] = self.normalize_by_attribute
        res['normalization_method'] = VectorRendererBase.normalize_method_to_string(self.normalization_method)
        res['st_dev_interval'] = self.st_dev_interval
        res['sampling_size'] = self.sampling_size
        res['exclusion_filter'] = self.exclusion_filter
        res['excluded_legend_group'] = self.excluded_legend_group.to_dict() if self.excluded_legend_group else None
        res['show_excluded_class'] = self.show_excluded_class
        res['is_graduated_symbol'] = self.is_graduated_symbol
        res['barrier_weight'] = self.barrier_weight
        res['sort_ascending'] = self.sort_ascending
        res['sampling_method'] = self.sampling_method
        res['background_symbol'] = self.background_symbol.to_dict() if self.background_symbol else None
        res['normalization_total'] = self.normalization_total
        res['flip_symbols'] = self.flip_symbols
        return res
