#!/usr/bin/env python
"""
Serializable object subclass

NEAR COMPLETE INTERPRETATION - all useful components
"""

from slyr_community.parser.object import Object
from slyr_community.parser.stream import Stream


class DotDensityFillSymbol(Object):
    """
    DotDensityFillSymbol
    """

    @staticmethod
    def cls_id():
        return '9a1eba10-cdf9-11d3-81eb-0080c79f0371'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.outline_symbol = None
        self.use_mask = False
        self.mask_exclude_in = False
        self.seed = 0
        self.fixed_placement = False
        self.markers = []
        self.dot_counts = []
        self.dot_size = 2
        self.dot_spacing = 0
        self.background_color = None
        self.fill_color = None
        self.symbol_level = 0

    def read(self, stream: Stream, version):
        self.fixed_placement = stream.read_uchar('fixed placement') != 0
        self.dot_spacing = stream.read_double('dot spacing')

        self.use_mask = stream.read_uchar('use mask') != 0

        self.fill_color = stream.read_object('fill color')  # unused?
        self.outline_symbol = stream.read_object('outline')

        stream.read_int('raster op', expected=13)
        self.symbol_level = stream.read_int('symbol_level')

        self.seed = stream.read_int('seed')
        self.dot_size = stream.read_double('dot size')
        self.mask_exclude_in = stream.read_uchar('mask exclude in') != 0

        marker_count = stream.read_int('marker count')
        for i in range(marker_count):
            self.markers.append(stream.read_object('marker {}'.format(i + 1)))
        for i in range(marker_count):
            self.dot_counts.append(stream.read_int('dot count {}'.format(i + 1)))

        self.background_color = stream.read_object('background color')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'fixed_placement': self.fixed_placement,
            'dot_spacing': self.dot_spacing,
            'outline_symbol': self.outline_symbol.to_dict() if self.outline_symbol else None,
            'mask_exclude_in': self.mask_exclude_in,
            'seed': self.seed,
            'markers': [m.to_dict() for m in self.markers],
            'dot_counts': self.dot_counts,
            'dot_size': self.dot_size,
            'background_color': self.background_color.to_dict() if self.background_color else None,
            'fill_color': self.fill_color.to_dict() if self.fill_color else None,
            'use_mask': self.use_mask,
            'symbol_level': self.symbol_level
        }
