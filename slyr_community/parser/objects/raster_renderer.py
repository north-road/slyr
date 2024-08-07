#!/usr/bin/env python
"""
Serializable object subclass
"""

from typing import Optional

from ..object import Object
from ..stream import Stream


class RasterRenderer(Object):
    """
    Base class for raster renderers
    """

    STRETCH_TYPE_NONE = 0
    STRETCH_TYPE_DEFAULT = 1
    STRETCH_TYPE_CUSTOM = 2
    STRETCH_TYPE_STDEV = 3
    STRETCH_TYPE_HISTOGRAM_EQUALIZE = 4
    STRETCH_TYPE_MINMAX = 5
    STRETCH_TYPE_HISTOGRAM_SPEC = 6
    STRETCH_TYPE_PERCENT_MINMAX = 7
    STRETCH_TYPE_ESRI = 8
    STRETCH_TYPE_COUNT = 9

    STATS_AREA_OF_VIEW = 0
    STATS_DATASET = 1
    STATS_GLOBAL = 2

    RESAMPLING_NEAREST_NEIGHBOR = 0
    RESAMPLING_BILINEAR = 1
    RESAMPLING_CUBIC = 2
    RESAMPLING_MAJORITY = 3
    RESAMPLING_BILINEAR_PLUS = 4

    @staticmethod
    def stretch_type_to_string(stretch) -> Optional[str]:
        """
        Converts a stretch type to a string
        """
        return {
            RasterRenderer.STRETCH_TYPE_NONE: 'none',
            RasterRenderer.STRETCH_TYPE_DEFAULT: 'default',
            RasterRenderer.STRETCH_TYPE_CUSTOM: 'custom',
            RasterRenderer.STRETCH_TYPE_STDEV: 'stdev',
            RasterRenderer.STRETCH_TYPE_HISTOGRAM_EQUALIZE:
                'histogram_equalize',
            RasterRenderer.STRETCH_TYPE_MINMAX: 'minmax',
            RasterRenderer.STRETCH_TYPE_HISTOGRAM_SPEC: 'histogram_spec',
            RasterRenderer.STRETCH_TYPE_PERCENT_MINMAX: 'percent_minmax',
            RasterRenderer.STRETCH_TYPE_ESRI: 'esri',
            RasterRenderer.STRETCH_TYPE_COUNT: 'count'
        }.get(stretch)

    @staticmethod
    def stats_type_to_string(stats) -> Optional[str]:
        """
        Converts a stats type to a string
        """
        return {
            RasterRenderer.STATS_AREA_OF_VIEW: 'area_of_view',
            RasterRenderer.STATS_DATASET: 'dataset',
            RasterRenderer.STATS_GLOBAL: 'global'
        }.get(stats)

    @staticmethod
    def resampling_type_to_string(resampling) -> Optional[str]:
        """
        Converts a resampling type to a string
        """
        return {
            RasterRenderer.RESAMPLING_NEAREST_NEIGHBOR: 'nearest_neighbor',
            RasterRenderer.RESAMPLING_BILINEAR: 'bilinear',
            RasterRenderer.RESAMPLING_CUBIC: 'cubic',
            RasterRenderer.RESAMPLING_MAJORITY: 'majority',
            RasterRenderer.RESAMPLING_BILINEAR_PLUS: 'bilinear_plus'
        }.get(resampling)

    def __init__(self):
        super().__init__()
        self.contrast = 0
        self.brightness = 0
        self.resampling_type = RasterRenderer.RESAMPLING_NEAREST_NEIGHBOR
        self.nodata_color = None
        self.primary_display_field = None
        self.alpha_band = None
        self.alpha_checked = False
        self.color_ramp = None

        self.should_read_display_props = False

    # pylint: disable=too-many-statements
    def read(self, stream: Stream, version):
        internal_version = stream.read_int('internal version',
                                           expected=(2, 3, 6, 7, 8, 9))

        #        if internal_version < 3 and self.__class__.__name__ in ('RasterRGBRenderer', 'RasterStretchColorRampRenderer'):
        #            self.should_read_display_props = False

        # pylint: disable=too-many-branches
        def handler(ref, size):
            if ref == 1:
                assert size == 4
                stream.read_int('unknown', expected=(0, 1))
            elif ref == 2:
                assert size == 4
                self.brightness = stream.read_int('brightness')
            elif ref == 3:
                assert size == 4
                self.contrast = stream.read_int('contrast')
            elif ref == 4:
                assert size == 4
                self.resampling_type = stream.read_int('resampling type')
            elif ref == 5:
                assert size == 4
                stream.read_int('unknown', expected=(0, 1))
            elif ref == 6:
                assert size == 0xffffffff
                self.nodata_color = stream.read_object('nodata color',
                                                       allow_reference=False)
            elif ref == 7:
                assert size == 24
                # some per band value?
                for i in range(3):
                    res = stream.read_int('unknown {}'.format(i + 1))
                    if res == 0:
                        stream.read_ushort('unknown a', expected=(0, 65504))
                        stream.read_ushort('unknown b', expected=(
                            0, 16, 16623, 49248, 49376))
                    elif res == 0xffffffff:
                        stream.read_ushort('unknown', expected=65535)
                        stream.read_ushort('unknown', expected=65519)
                    elif res == 0xffe00000:
                        stream.read_ushort('unknown', expected=65535)
                        stream.read_ushort('unknown', expected=16879)
                    elif res == 0xffc00000:
                        stream.read_ushort('unknown', expected=65535)
                        stream.read_ushort('unknown', expected=16863)
                    elif res == 0xe0000000:
                        stream.read_ushort('unknown', expected=65535)
                        stream.read_ushort('unknown', expected=51183)
                    else:
                        stream.read_ushort('unknown')
                        stream.read_ushort('unknown')
            else:
                assert False, 'Unknown property ref {}'.format(ref)

        # pylint: enable=too-many-branches

        stream.read_indexed_properties(handler)
        stream.read_ushort('unknown', expected=65535)
        stream.read_ushort('unknown', expected=65535)

        if internal_version > 3:
            # NOT present for
            # raster layer v7, RasterUniqueValueRenderer v2, renderer v2
            # raster layer v7, RasterUniqueValueRenderer v1, renderer v2

            # present for
            # raster layer v13, RasterRGBRenderer v4, renderer v3
            # raster layer v13, RasterRGBRenderer v4, renderer v7
            # raster layer v16, RasterRGBRenderer v5, renderer v8
            # raster layer v18, RasterStretchColorRampRenderer v10, renderer v9
            # raster layer v17, RasterStretchColorRampRenderer v9, renderer v9

            stream.read_ushort('unknown', expected=(0, 65535))

            self.primary_display_field = stream.read_ushort(
                'primary display field') != 65535
            stream.read_ushort('unknown flag relating to display field')
            res = stream.read_int('alpha band')
            self.alpha_band = None if res == 0xffffffff else res + 1

        if internal_version > 7:
            self.alpha_checked = stream.read_ushort('alpha checked') != 0

        if internal_version >= 7:
            # present for
            # raster layer v13, RasterRGBRenderer v4, renderer v7
            # raster layer v16, RasterRGBRenderer v5, renderer v8
            # raster layer v18, RasterStretchColorRampRenderer v10, renderer v9
            # raster layer v17, RasterStretchColorRampRenderer v9, renderer v9

            # not present for
            # raster layer v7, RasterUniqueValueRenderer v2, renderer v2
            stream.read_uchar('unknown', expected=(0, 255))

        if internal_version > 8:
            self.color_ramp = stream.read_object('ramp')

    # pylint: enable=too-many-statements

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'brightness': self.brightness,
            'contrast': self.contrast,
            'resampling_type': RasterRenderer.resampling_type_to_string(
                self.resampling_type),
            'nodata_color': self.nodata_color.to_dict() if self.nodata_color else None,
            'primary_display_field': self.primary_display_field,
            'alpha_band': self.alpha_band,
            'alpha_checked': self.alpha_checked
        }
