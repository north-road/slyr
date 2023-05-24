#!/usr/bin/env python
"""
Serializable object subclass
"""

from .raster_renderer import RasterRenderer
from ..object import Object
from ..stream import Stream


class RasterStretchColorRampRenderer(RasterRenderer):
    """
    RasterStretchColorRampRenderer
    """

    @staticmethod
    def cls_id():
        return 'a301a3b2-74d7-11d2-9f29-00c04f8ed1d7'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.band = 1
        self.color_ramp = None
        self.histogram = None
        self.legend = None
        self.background_value = None
        self.background_color = None
        self.display_background_value = False
        self.stretch_type = RasterRenderer.STRETCH_TYPE_NONE
        self.stretch_low = 0
        self.stretch_high = 0
        self.stats_type = RasterRenderer.STATS_DATASET
        self.stretch_standard_deviations = 2.5
        self.apply_gamma = False
        self.gamma = 1
        self.use_hillshade = False
        self.hillshade_z = 0
        self.invert_stretch = False
        self.sigmoid_strength = 4
        self.number_of_labels = 3
        self.min_value = 0
        self.max_value = 0

        self.legend_classes = 0
        self.has_legend_text = False

    @staticmethod
    def clsid():
        return 'a301a3b2-74d7-11d2-9f29-00c04f8ed1d7'

    @staticmethod
    def compatible_versions():
        return [3, 4, 6, 9, 10]

    def read(self, stream: Stream, version):
        stream.read_ushort('unknown', expected=0)
        stream.read_string('name?')

        # pylint: disable=too-many-branches, too-many-statements
        def handler(ref, size):
            if ref == 1:
                assert size == 4
                self.band = stream.read_int('band') + 1
            elif ref == 2:
                # maybe custom stretch settings?
                stream.read(size)
            elif ref == 3:
                assert size == 4
                self.stretch_type = stream.read_int('stretch type')
            elif ref == 4:
                assert size == 8
                self.stretch_standard_deviations = stream.read_double(
                    'stretch standard deviations')
            elif ref == 5:
                assert size == 4
                self.invert_stretch = stream.read_int('invert stretch') != 0
            elif ref == 6:
                assert size == 8
                self.background_value = stream.read_double('background value')
            elif ref == 7:
                assert size == 0xffffffff
                self.color_ramp = stream.read_object('color ramp',
                                                     allow_reference=False)
            elif ref == 8:
                assert size == 0xffffffff
                self.background_color = stream.read_object('background color',
                                                           allow_reference=False)
            elif ref == 9:
                assert size == 0xffffffff
                self.legend = stream.read_object('legend group?',
                                                 allow_reference=False)
            elif ref == 10:
                assert size == 4
                self.display_background_value = stream.read_int(
                    'display background value') != 0
            elif ref == 11:
                assert size == 4
                stream.read_int('unknown', expected=1)
            elif ref == 12:
                assert size == 2
                stream.read_ushort('unknown', expected=0)
            elif ref == 13:
                assert size == 16
                self.min_value = stream.read_double('min value')
                self.max_value = stream.read_double('max value')
            elif ref == 14:
                assert size == 4
                self.stats_type = stream.read_int('stats type')
            elif ref == 15:
                assert size == 4
                self.use_hillshade = stream.read_int('use hillshade') != 0
            elif ref == 16:
                assert size == 8
                self.hillshade_z = stream.read_double('hillshade z')
            elif ref == 17:
                assert size == 0xffffffff
                self.histogram = stream.read_object('histogram',
                                                    allow_reference=False)
            elif ref == 18:
                assert size == 4
                self.apply_gamma = stream.read_int('apply gamma') != 0
            elif ref == 19:
                assert size == 8
                self.gamma = stream.read_double('gamma')
            elif ref == 20:
                assert size == 4
                self.number_of_labels = stream.read_int('number of labels')
            elif ref == 21:
                assert size == 4
                self.legend_classes = stream.read_int('legend classes')
            elif ref == 22:
                assert size == 4
                self.has_legend_text = stream.read_int('has legend text') != 0

                # my gosh, way to stick to your standards...
                for i in range(self.legend_classes):
                    stream.read_double('value')
                    if self.has_legend_text:
                        stream.read_string('label')
                self.stretch_low = stream.read_double('stretch low')
                self.stretch_high = stream.read_double('stretch high')
            else:
                assert False, 'Unknown property ref {}'.format(ref)
        # pylint: enable=too-many-branches, too-many-statements

        stream.read_indexed_properties(handler)
        stream.read_ushort('unknown', expected=65535)
        stream.read_ushort('unknown', expected=65535)

        if version > 6:
            stream.read_ushort('unknown', expected=65535)
            stream.read_ushort('unknown', expected=65519)
            stream.read_ushort('unknown', expected=65535)
            stream.read_ushort('unknown', expected=65535)
            stream.read_ushort('unknown', expected=65535)
            stream.read_ushort('unknown', expected=65519)
            self.sigmoid_strength = stream.read_int('sigmoid strength') + 1
            stream.read_ushort('unknown', expected=65535)
            stream.read_ushort('unknown', expected=65535)
        if version > 9:
            stream.read_ushort('unknown', expected=65535)
            stream.read_ushort('unknown', expected=65535)

        super().read(stream, 1 if version < 4 else 2)

    def to_dict(self):  # pylint: disable=method-hidden
        res = super().to_dict()
        res['band'] = self.band
        res['histogram'] = self.histogram.to_dict() if self.histogram else None
        res[
            'color_ramp'] = self.color_ramp.to_dict() if self.color_ramp else None
        res['legend'] = self.legend.to_dict() if self.legend else None
        res['background_value'] = self.background_value
        res[
            'background_color'] = self.background_color.to_dict() if self.background_color else None
        res['display_background_value'] = self.display_background_value
        res['stretch_type'] = RasterRenderer.stretch_type_to_string(
            self.stretch_type)
        res['stretch_low'] = self.stretch_low
        res['stretch_high'] = self.stretch_high
        res['stats_type'] = RasterRenderer.stats_type_to_string(
            self.stats_type)
        res['stretch_standard_deviations'] = self.stretch_standard_deviations
        res['invert_stretch'] = self.invert_stretch
        res['apply_gamma'] = self.apply_gamma
        res['gamma'] = self.gamma
        res['use_hillshade'] = self.use_hillshade
        res['hillshade_z'] = self.hillshade_z
        res['sigmoid_strength'] = self.sigmoid_strength
        res['number_of_labels'] = self.number_of_labels
        res['min_value'] = self.min_value
        res['max_value'] = self.max_value
        return res


class RedrawLegendClass(Object):
    """
    RedrawLegendClass
    """

    @staticmethod
    def cls_id():
        return 'a12e0ff1-ac90-445c-b335-ac2c6f54d18b'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.label = ''
        self.symbol = None
        self.format = None

    @staticmethod
    def compatible_versions():
        return [1, 2]

    def read(self, stream: Stream, version):
        self.symbol = stream.read_object('symbol')

        self.label = stream.read_string('legend label')
        stream.read_string('unknown', expected='')

        self.format = stream.read_object('legend class format')

        if version > 1:
            stream.read_int('unknown flag', expected=(1, 0xffffffff))

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'label': self.label,
            'symbol': self.symbol.to_dict() if self.symbol else None,
            'format': self.format.to_dict() if self.format else None
        }
