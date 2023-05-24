#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..stream import Stream
from .raster_renderer import RasterRenderer
from .classification_utils import ClassificationUtils


class RasterClassifyColorRampRenderer(RasterRenderer):
    """
    RasterClassifyColorRampRenderer
    """

    @staticmethod
    def cls_id():
        return 'ce8b2f44-a027-11d2-aae7-00c04fa33416'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.classifier = None
        self.ramp_name = ''
        self.source_field_name = ''
        self.legend_group = None
        self.number_format = None
        self.legend = None
        self.unique_values = None
        self.breaks = []
        self.show_class_breaks_using_cell_values = False
        self.use_hillshade = False
        self.hillshade_z = 0
        self.normalization_field = ''
        self.sort_classes_ascending = True
        self.deviation_interval = 0
        self.excluded_show_class = False
        self.allow_interactive_display = False
        self.excluded_ranges = []
        self.excluded_values = []

    @staticmethod
    def compatible_versions():
        return [3, 4, 5]

    def read(self, stream: Stream, version):
        stream.read_ushort('unknown', expected=0)
        self.source_field_name = stream.read_string('class field')
        self.normalization_field = stream.read_string('normalization field')

        res = stream.read_uchar('unknown')  # in (0, 1)
        if res:
            c = stream.read_raw_clsid('classifier')
            assert c in ClassificationUtils.CLSID_TO_CLASSIFIER, c
            self.classifier = ClassificationUtils.CLSID_TO_CLASSIFIER[c]

        self.ramp_name = stream.read_string('ramp name')

        # this is PROBABLY count of legend groups, but always seems to be 1
        count  = stream.read_int('legend group count', expected=(0, 1))
        if count:
            self.legend_group = stream.read_object('legend group')

        stream.read_int('unknown', expected=0)
        stream.read_int('unknown', expected=0)
        stream.read_int('unknown', expected=0)
        stream.read_int('unknown', expected=0)

        class_count = stream.read_int('class count')
        breaks = []
        for i in range(class_count):
            breaks.append(stream.read_double('max {}'.format(i + 1)))
        self.breaks = breaks

        self.sort_classes_ascending = stream.read_ushort('sort classes ascending') != 0
        self.number_format = stream.read_object('number format')
        self.show_class_breaks_using_cell_values = stream.read_ushort('show class breaks using cell values') != 0
        self.deviation_interval = stream.read_double('deviation interval')
        has_excluded_values = stream.read_ushort('has excluded values') != 0
        stream.read_ushort('unknown', expected=0)
        stream.read_int('unknown', expected=0)
        stream.read_int('unknown', expected=0)
        stream.read_int('unknown', expected=0)
        if has_excluded_values:
            count = stream.read_int('excluded range count')
            for i in range(count):
                self.excluded_ranges.append(stream.read_double('range {}'.format(i + 1)))

        has_excluded_ranges = stream.read_ushort('has excluded ranges') != 0
        stream.read_ushort('unknown', expected=0)
        stream.read_int('unknown', expected=0)
        stream.read_int('unknown', expected=0)
        stream.read_int('unknown', expected=0)

        if has_excluded_ranges:
            count = stream.read_int('excluded range count')
            for i in range(count):
                self.excluded_values.append(stream.read_double('range {}'.format(i + 1)))

        self.excluded_show_class = stream.read_ushort('excluded show class') != 0
        self.legend = stream.read_object('excluded legend class')

        if version <= 3:
            self.should_read_display_props = False

        if version > 3:
            self.unique_values = stream.read_object('unique values')

        # some version 4 don't have this
        # raster layer v11 doesn't
        # v13 does
        # v7 does
        # v16 does
        if version >= 4 and stream.sniff_index_properties_header(): # and stream.custom_props.get('raster_layer_version') != 11:
            def handler(ref, size):
                if ref == 1:
                    assert size == 4
                    self.use_hillshade = stream.read_int('use hillshade') != 0
                elif ref == 2:
                    assert size == 8
                    self.hillshade_z = stream.read_double('hillshade z')
                elif ref == 37:
                    assert size == 2
                    self.allow_interactive_display = stream.read_ushort('allow interactive display') != 0
                else:
                    assert False, 'Unknown property ref {}'.format(ref)

            stream.read_indexed_properties(handler)
            stream.read_ushort('unknown', expected=65535)
            stream.read_ushort('unknown', expected=65535)

        if version > 4:
            stream.read_ushort('unknown', expected=0)
        super().read(stream, 2)

    def to_dict(self):  # pylint: disable=method-hidden
        res = super().to_dict()
        res['classifier'] = ClassificationUtils.classifier_to_string(self.classifier)
        res['ramp_name'] = self.ramp_name
        res['source_field_name'] = self.source_field_name
        res['legend_group'] = self.legend_group.to_dict() if self.legend_group else None
        res['number_format'] = self.number_format.to_dict() if self.number_format else None
        res['legend'] = self.legend.to_dict() if self.legend else None
        res['unique_values'] = self.unique_values.to_dict() if self.unique_values else None
        res['breaks'] = self.breaks
        res['show_class_breaks_using_cell_values'] = self.show_class_breaks_using_cell_values
        res['use_hillshade'] = self.use_hillshade
        res['hillshade_z'] = self.hillshade_z
        res['normalization_field'] = self.normalization_field
        res['sort_classes_ascending'] = self.sort_classes_ascending
        res['deviation_interval'] = self.deviation_interval
        res['excluded_show_class'] = self.excluded_show_class
        res['allow_interactive_display'] = self.allow_interactive_display
        res['excluded_ranges'] = self.excluded_ranges
        res['excluded_values'] = self.excluded_values
        return res
