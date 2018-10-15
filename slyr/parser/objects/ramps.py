#!/usr/bin/env python
"""
Color ramps
"""

from slyr.parser.object import Object
from slyr.parser.stream import Stream


class ColorRamp(Object):
    """
    Base class for color ramps
    """

    def __init__(self):
        super().__init__()
        self.ramp_name_type = ''

    def read_ramp_name_type(self, stream: Stream):
        """
        Reads the ramp name type from a stream
        """
        name_length = stream.read_int('name size')
        self.ramp_name_type = stream.read(name_length * 2).decode('utf-16')
        stream.log('Ramp name \'{}\''.format(self.ramp_name_type), name_length * 2)

        stream.read(2)

    def to_dict(self) -> dict:
        """
        Returns a dictionary representation of the color
        :return:
        """
        return {}


class RandomColorRamp(ColorRamp):
    """
    Random color ramp
    """

    def __init__(self):
        super().__init__()
        self.same_everywhere = False
        self.val_min = 0
        self.val_max = 100
        self.sat_min = 0
        self.sat_max = 100
        self.hue_min = 0
        self.hue_max = 360

    @staticmethod
    def guid():
        return 'beb87094-c0b4-11d0-8379-080009b996cc'

    def read(self, stream, version):
        self.read_ramp_name_type(stream)

        stream.read(4)
        self.same_everywhere = bool(stream.read_ushort('Same everywhere'))
        stream.read(4)
        self.val_min = stream.read_ushort('val min')
        self.val_max = stream.read_ushort('val max')
        self.sat_min = stream.read_ushort('sat min')
        self.sat_max = stream.read_ushort('sat max')
        self.hue_min = stream.read_ushort('hue min')
        self.hue_max = stream.read_ushort('hue max')

    def to_dict(self):
        return {'value_range': [self.val_min, self.val_max], 'saturation_range': [self.sat_min, self.sat_max],
                'hue_range': [self.hue_min, self.hue_max], 'same_everywhere': self.same_everywhere,
                'ramp_name_type': self.ramp_name_type}


class PresetColorRamp(ColorRamp):
    """
    Preset color ramp
    """

    def __init__(self):
        super().__init__()
        self.ramp_name_type = ''
        self.colors = []

    @staticmethod
    def guid():
        return 'beb8709a-c0b4-11d0-8379-080009b996cc'

    def children(self):
        res = super().children()
        res.extend(self.colors)
        return res

    def read(self, stream, version):
        self.read_ramp_name_type(stream)

        stream.read(4)

        color_count = stream.read_uint('Number of colors')
        for i in range(color_count):
            self.colors.append(stream.read_object('Color {}'.format(i + 1)))

    def to_dict(self):
        return {'colors': [c.to_dict() for c in self.colors],
                'ramp_name_type': self.ramp_name_type}


class MultiPartColorRamp(ColorRamp):
    """
    Multi-part color ramp
    """

    def __init__(self):
        super().__init__()
        self.parts = []
        self.part_lengths = []

    @staticmethod
    def guid():
        return 'beb87099-c0b4-11d0-8379-080009b996cc'

    @staticmethod
    def compatible_versions():
        return [2]

    def children(self):
        res = super().children()
        for p in self.parts:
            if p:
                res.append(p)
        return res

    def read(self, stream, version):
        self.read_ramp_name_type(stream)
        count = stream.read_uint('Number of parts')
        for i in range(count):
            self.parts.append(stream.read_object('Part {}'.format(i + 1)))
        for i in range(count):
            self.part_lengths.append(stream.read_double('Length {}'.format(i + 1)))

    def to_dict(self):
        return {'parts': [p.to_dict() for p in self.parts],
                'part_lengths': self.part_lengths,
                'ramp_name_type': self.ramp_name_type}


class AlgorithmicColorRamp(ColorRamp):
    """
    Algorithmic color ramp
    """

    ALGORITHM_CIELAB = 1
    ALGORITHM_HSV = 0
    ALGORITHM_LABLCH = 2

    def __init__(self):
        super().__init__()
        self.ramp_name_type = ''
        self.algorithm = None
        self.color1 = None
        self.color2 = None

    @staticmethod
    def guid():
        return 'beb8709b-c0b4-11d0-8379-080009b996cc'

    @staticmethod
    def compatible_versions():
        return [1]

    def children(self):
        res = super().children()
        if self.color1:
            res.append(self.color1)
        if self.color2:
            res.append(self.color2)
        return res

    def read(self, stream, version):
        self.read_ramp_name_type(stream)
        self.algorithm = stream.read_uint('Algorithm')
        self.color1 = stream.read_object('Color 1')
        self.color2 = stream.read_object('Color 2')

    def to_dict(self):
        return {'color1': self.color1.to_dict(),
                'color2': self.color2.to_dict(),
                'algorithm': self.algorithm,
                'ramp_name_type': self.ramp_name_type}
